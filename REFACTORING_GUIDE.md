# DnD Spell Scraper Refactoring Guide

## Current State Analysis

### Problems Identified
- **90% code duplication** between `getSpells.py` and `getSpells2024.py`
- **Mixed concerns** - scraping, parsing, and database operations in one place
- **Hard-coded URLs and parsing logic**
- **Inconsistent error handling**
- **Model differences** - Spell2014 has `spellSchool`, Spell2024 has `spellType`

### Code Smells
1. **Duplicate Code** - Same scraping logic repeated
2. **Long Method** - `handle()` method does too many things
3. **Magic Numbers/Strings** - Hard-coded attribute indices (`atr1`, `atr2`, etc.)
4. **Tight Coupling** - Scraping logic tied to specific models
5. **No Error Recovery** - Fails completely on single spell error

## Refactoring Strategy: Clean Architecture

### Separation of Concerns
```
┌─────────────────┐
│ Command Layer   │ ← Thin management commands
├─────────────────┤
│ Service Layer   │ ← Business logic (scraping)
├─────────────────┤
│ Data Layer      │ ← Models (already exists)
└─────────────────┘
```

### SOLID Principles Application
- **S**ingle Responsibility: Each class has one job
- **O**pen/Closed: Easy to add new spell versions
- **L**iskov Substitution: 2014/2024 scrapers interchangeable
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concrete classes

## Step-by-Step Implementation Plan

### Phase 1: Create Base Architecture

#### Step 1.1: Create Services Directory Structure
```bash
mkdir -p spells/services
touch spells/services/__init__.py
```

#### Step 1.2: Create Data Transfer Object (DTO)
**File:** `spells/services/spell_data.py`

**Purpose:** Clean data container to decouple scraping from models

**What to implement:**
- `SpellData` class with all spell attributes
- Constructor with sensible defaults
- No business logic, just data storage

**Key attributes:**
- name, source, spell_level, spell_school_or_type
- casting_time, spell_range, components, duration
- description, spell_lists (as set)

#### Step 1.3: Create Abstract Base Scraper
**File:** `spells/services/base_scraper.py`

**Purpose:** Define common scraping interface and shared functionality

**Abstract methods to define:**
- `get_base_url()` → str
- `get_spell_model()` → Django Model class
- `get_spell_list_model()` → Django Model class
- `extract_spell_lists(soup)` → Set[str]
- `parse_spell_level_and_school(attributes)` → Tuple[str, str]

**Concrete methods to implement:**
- `fetch_spell_urls()` → List[str]
- `scrape_spell(url)` → Optional[SpellData]
- `save_spell(spell_data)` → bool
- `_extract_spell_name(soup)` → str
- `_extract_attributes(soup)` → Dict[str, str]
- `_build_description(attributes, start_index)` → str

**Learning Focus:**
- Abstract Base Classes (ABC)
- Template Method Pattern
- Error handling with logging

### Phase 2: Implement Version-Specific Scrapers

#### Step 2.1: Create 2014 Scraper
**File:** `spells/services/spell_scraper_2014.py`

**Inherits from:** `BaseSpellScraper`

**Implement these methods:**
- `get_base_url()` → `'https://dnd5e.wikidot.com/spells'`
- `get_spell_model()` → `Spell2014`
- `get_spell_list_model()` → `SpellList2014`
- `extract_spell_lists()` → Parse "Spell Lists:" text
- `parse_spell_level_and_school()` → Handle cantrip vs regular spells

**Key differences from 2024:**
- Uses HTTPS
- Different spell list extraction logic
- Separates level and school differently

#### Step 2.2: Create 2024 Scraper
**File:** `spells/services/spell_scraper_2024.py`

**Inherits from:** `BaseSpellScraper`

**Implement these methods:**
- `get_base_url()` → `'http://dnd2024.wikidot.com/spell:all'`
- `get_spell_model()` → `Spell2024`
- `get_spell_list_model()` → `SpellList2024`
- `extract_spell_lists()` → Parse regex from `<em>` tags
- `parse_spell_level_and_school()` → Different parsing logic

**Key differences from 2014:**
- Uses HTTP
- Regex-based spell list extraction
- Different URL structure

### Phase 3: Refactor Management Commands

#### Step 3.1: Create Unified Command
**File:** `spells/management/commands/scrape_spells.py`

**Purpose:** Single command that can scrape both versions

**Command structure:**
```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--version', choices=['2014', '2024', 'both'])
    
    def handle(self, *args, **options):
        # Thin layer - just orchestrates scraper
```

**Learning Focus:**
- Command pattern
- Dependency injection
- Factory pattern for scraper selection

#### Step 3.2: Update Existing Commands (Optional)
- Modify existing commands to use new scrapers
- Keep for backward compatibility
- Make them thin wrappers

### Phase 4: Add Improvements

#### Step 4.1: Add Configuration
**File:** `spells/services/scraper_config.py`

**Purpose:** Centralize configuration

**What to include:**
- URL mappings
- Timeout settings
- Retry logic configuration
- Logging configuration

#### Step 4.2: Add Error Handling
**Improvements to add:**
- Retry logic for failed requests
- Graceful handling of malformed HTML
- Continue scraping even if one spell fails
- Detailed error reporting

#### Step 4.3: Add Progress Tracking
- Progress bars for long operations
- Statistics reporting (success/failure counts)
- Resume capability for interrupted scraping

## Learning Exercises

### Exercise 1: Identify Patterns
**Task:** Compare the two existing files line by line
**Goal:** List every duplicated piece of code
**Learning:** Pattern recognition, code smell identification

### Exercise 2: Extract Common Code
**Task:** Create a list of what should be in the base class
**Goal:** Understand abstraction levels
**Learning:** Interface design, abstraction

### Exercise 3: Handle Differences
**Task:** Identify what's truly different between versions
**Goal:** Minimize version-specific code
**Learning:** Polymorphism, strategy pattern

### Exercise 4: Test-Driven Development
**Task:** Write tests before implementing
**Goal:** Ensure refactoring doesn't break functionality
**Learning:** TDD, regression testing

## Testing Strategy

### Unit Tests to Write
1. **SpellData tests** - Data validation
2. **Base scraper tests** - Common functionality
3. **Version-specific tests** - Parsing differences
4. **Integration tests** - End-to-end scraping

### Test Files to Create
- `tests/test_spell_data.py`
- `tests/test_base_scraper.py`
- `tests/test_spell_scraper_2014.py`
- `tests/test_spell_scraper_2024.py`

## Implementation Order

### Week 1: Foundation
1. Create directory structure
2. Implement SpellData class
3. Start base scraper (abstract methods only)

### Week 2: Core Logic
1. Implement base scraper concrete methods
2. Create 2014 scraper
3. Test 2014 scraper thoroughly

### Week 3: Extension
1. Create 2024 scraper
2. Create unified command
3. Add error handling

### Week 4: Polish
1. Add configuration
2. Improve error messages
3. Add progress tracking
4. Write comprehensive tests

## Key Learning Concepts

### Design Patterns Used
- **Template Method** - Base scraper defines algorithm, subclasses fill details
- **Factory** - Create appropriate scraper based on version
- **Strategy** - Different parsing strategies for different versions
- **Command** - Management commands as executable objects

### Clean Code Principles
- **DRY** - Don't Repeat Yourself
- **SOLID** - Object-oriented design principles
- **YAGNI** - You Aren't Gonna Need It
- **KISS** - Keep It Simple, Stupid

### Python Best Practices
- Type hints for better code documentation
- Abstract base classes for interface definition
- Logging instead of print statements
- Exception handling with specific exception types
- Context managers for resource management

## Common Pitfalls to Avoid

1. **Over-engineering** - Don't add complexity you don't need
2. **Premature optimization** - Make it work first, then make it fast
3. **Tight coupling** - Keep classes independent
4. **God objects** - Don't put everything in one class
5. **Magic numbers** - Use constants for hard-coded values

## Success Metrics

### Code Quality Improvements
- [ ] Reduce code duplication from 90% to <10%
- [ ] Separate concerns into distinct layers
- [ ] Add comprehensive error handling
- [ ] Achieve >80% test coverage

### Maintainability Improvements
- [ ] Easy to add new spell versions
- [ ] Clear separation of responsibilities
- [ ] Self-documenting code structure
- [ ] Consistent error handling

### Learning Outcomes
- [ ] Understand clean architecture principles
- [ ] Practice SOLID design principles
- [ ] Learn abstract base classes
- [ ] Implement design patterns
- [ ] Write maintainable, testable code

## Next Steps After Refactoring

1. **Add new features** easily (filtering, search, etc.)
2. **Performance optimization** (caching, async requests)
3. **Data validation** (schema validation, data integrity)
4. **API integration** (REST API for spell data)
5. **Monitoring** (metrics, health checks)

---

**Remember:** The goal is not just to reduce duplication, but to create a maintainable, extensible system that follows clean code principles. Take your time, write tests, and focus on learning the underlying concepts.