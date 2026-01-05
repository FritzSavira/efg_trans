# **Development Guidelines Summary**

This document defines the documentation strategy for the `ama_browser` project, ensuring consistency, clarity, and effective collaboration.

## **1. Centralized Documentation**
All project documentation is stored in the `docs/` directory with the following structure:
```
your_project/
├── docs/
│   ├── adr/ (Architectural Decision Records)
│   ├── CHANGELOG.md (chronological changes)
│   ├── DEV_TASKS.md (current/upcoming tasks)
│   ├── CODING_STYLE.md
│   ├── PROJECT_BRIEFING.md
│   ├── DEVELOPMENT_GUIDELINES.md
│   └── guides/ (additional guides)
└── ... (project code)
```

## **2. Documentation Types & Purpose**
| **Document** | **Focus** | **Content** | **Lifecycle** | **Interlinking** |
|--------------|-----------|------------|--------------|------------------|
| **ADRs** (`docs/adr/`) | *Why* behind major decisions | Context, decision, rationale, consequences | Created before/during implementation; mostly immutable | Referenced in `CHANGELOG.md`|
| **CHANGELOG.md** | *What* changed and when | Chronological history of changes | Updated after completion | Links to ADRs and tasks |
| **DEV_TASKS.md** | *What* needs to be done | Task status (TODO/In Progress/Done). For complex features, a detailed `DEV_TASKS-xxxx.md` file is created, which **must use Markdown checkboxes (`- [ ]`)** to track progress. | Continuously updated after completion of each Phase | Links to ADRs |

## **3. Interlinking Strategy**
- **ADR → CHANGELOG:** Reference ADRs in changelog entries.
- **DEV_TASKS → ADR:** Link tasks to relevant ADRs.
- **CHANGELOG → DEV_TASKS:** Mark tasks as "Done" -> [x].

## **4. Developer Workflow**
1. **Before starting a major change:**
   - Check if an ADR is needed; create it if required.
   - For complex tasks, create a corresponding `DEV_TASKS-xxxx.md` file.
2. **During development:**
   - Update task status in `DEV_TASKS-xxxx.md` file and check off completed items.
3. **Before completion:**
   - Test thoroughly.
4. **Upon completion:**
   - Update `CHANGELOG.md` with details and ADR references.
   - Mark tasks as "Done" in `DEV_TASKS-xxxx.md`.

## **5. Testing Guidelines**
### **Principles**
- Test early, often, and reproducibly.
- Automate where possible; manually test UX/edge cases.

### **Execution**
1. **Prerequisites:**
   - Activate virtual environment.
   - Install dependencies (`pip install -r requirements.txt`).
2. **Run tests:**
   ```bash
   pytest  # or python -m pytest (recommended)
   ```
3. **Expected outcome:** All tests pass; failures must be resolved.

### **Test Types**
| **Type** | **Purpose** | **Scope** | **Best Practices** |
|----------|------------|-----------|------------------|
| **Unit Tests** | Verify individual functions | Smallest components | High coverage; mock dependencies |
| **Integration Tests** | Verify module interactions | Component interfaces | Use real dependencies where possible |
| **E2E/UI Tests** | Validate full user flows | Entire application | Use tools like Selenium; focus on critical paths |
| **Manual Tests** | Catch UX/edge-case issues | Any part of the app | Document test cases and expected results |

### **Test Plan Documentation**
For major changes, include:
- Test objectives, preconditions, steps, expected results, edge cases.

## **6. Code Quality**
- **Rule:** All code **MUST** comply with `docs/CODING_STYLE.md`.
- **Action:** Ensure adherence before committing (naming, formatting, refactoring).

This summary retains all key information while improving conciseness for experienced developers.