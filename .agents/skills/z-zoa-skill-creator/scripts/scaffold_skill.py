#!/usr/bin/env python3
"""
Z-ZOA Skill Scaffolder & Auditor (`scaffold_skill.py`)

Creates and audits agent skills complying with Z-ZOA Calculation Room standards:
- Rule #1: Provenance tracking (SHA-256)
- Rule #2: Astropy unit typing
- Rule #3: Cosmology lock
- Rule #4: Holdout boundary isolation
- Antigravity/Gemini YAML frontmatter specification
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_NAME_REGEX = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

def validate_skill_name(name: str) -> None:
    if len(name) > 64:
        raise ValueError(f"Skill name '{name}' exceeds maximum length of 64 characters.")
    if not SKILL_NAME_REGEX.match(name):
        raise ValueError(
            f"Invalid skill name '{name}'. Must consist of lowercase alphanumeric characters "
            "and hyphens, starting and ending with an alphanumeric character."
        )

def validate_description(desc: str) -> None:
    if len(desc) > 1024:
        raise ValueError(f"Skill description exceeds 1024 characters (got {len(desc)}).")
    if len(desc.strip()) < 10:
        raise ValueError("Skill description is too short (must be at least 10 characters).")

def cmd_create(args) -> dict:
    name = args.name.lower().strip()
    validate_skill_name(name)
    description = args.description.strip()
    validate_description(description)

    title = args.title or name.replace("-", " ").title()
    script_name = f"{name.replace('-', '_')}_cli"

    # Determine target directory
    if args.install_path:
        base_dir = Path(args.install_path)
    else:
        # Default to local .agents/skills/ in workspace or current dir
        base_dir = Path(".agents") / "skills"

    skill_dir = base_dir / name
    if skill_dir.exists() and not args.force:
        raise FileExistsError(f"Skill directory already exists at {skill_dir}. Use --force to overwrite.")

    skill_dir.mkdir(parents=True, exist_ok=True)

    # Read templates
    ref_dir = Path(__file__).resolve().parent.parent / "references"
    skill_template_path = ref_dir / "zoa_skill_template.md"
    script_template_path = ref_dir / "zoa_script_template.py"

    if skill_template_path.exists():
        template_text = skill_template_path.read_text(encoding="utf-8")
    else:
        # Fallback inline template
        template_text = (
            "---\n"
            "name: {SKILL_NAME}\n"
            "description: >-\n"
            "  {SKILL_DESCRIPTION}\n"
            "---\n\n"
            "# {SKILL_TITLE}\n\n"
            "## Overview\n\n{BRIEF_DESCRIPTION}\n\n"
            "## Z-ZOA Architectural Standards\n\n"
            "1. **Provenance (Rule #1)**: Immutable SHA-256 digests recorded.\n"
            "2. **Astropy Units (Rule #2)**: Untyped floats rejected.\n"
            "3. **Cosmology Lock (Rule #3)**: Uses standard cosmological parameters.\n"
            "4. **Holdout Defense (Rule #4)**: Sealed validation catalogues.\n\n"
            "## Quick Start\n\n```powershell\npython scripts/{SCRIPT_NAME}.py --help\n```\n"
        )

    # Populate SKILL.md
    skill_md_content = template_text.replace("{SKILL_NAME}", name)
    skill_md_content = skill_md_content.replace("{SKILL_DESCRIPTION}", description)
    skill_md_content = skill_md_content.replace("{SKILL_TITLE}", title)
    skill_md_content = skill_md_content.replace("{BRIEF_DESCRIPTION}", description)
    skill_md_content = skill_md_content.replace("{SCRIPT_NAME}", script_name)
    skill_md_content = skill_md_content.replace(
        "{DEPENDENCIES_LIST}",
        args.dependencies if args.dependencies else "None",
    )

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_md_content, encoding="utf-8")

    created_files = [str(skill_file)]

    # Generate starter script if requested
    if args.with_script:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        target_script = scripts_dir / f"{script_name}.py"

        if script_template_path.exists():
            script_content = script_template_path.read_text(encoding="utf-8")
        else:
            script_content = "#!/usr/bin/env python3\n# Z-ZOA Script\n"

        target_script.write_text(script_content, encoding="utf-8")
        created_files.append(str(target_script))

    print(f"Skill '{name}' created successfully at: {skill_dir.resolve()}")
    for f in created_files:
        print(f"  + {f}")

    return {
        "status": "SUCCESS",
        "skill_name": name,
        "skill_directory": str(skill_dir.resolve()),
        "created_files": created_files,
    }

def cmd_audit(args) -> dict:
    skill_path = Path(args.skill_path).resolve()
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path does not exist: {skill_path}")

    skill_md = skill_path / "SKILL.md"
    issues = []
    checks = []

    # 1. Check SKILL.md exists
    if not skill_md.exists():
        issues.append("Missing SKILL.md file.")
        checks.append({"check": "skill_md_exists", "status": "FAIL"})
    else:
        checks.append({"check": "skill_md_exists", "status": "PASS"})
        content = skill_md.read_text(encoding="utf-8")

        # 2. Check frontmatter
        if not content.startswith("---"):
            issues.append("SKILL.md must begin with YAML frontmatter delimiter '---'.")
            checks.append({"check": "frontmatter_start", "status": "FAIL"})
        else:
            checks.append({"check": "frontmatter_start", "status": "PASS"})

        name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", content, re.MULTILINE)
        if not name_match:
            issues.append("YAML frontmatter missing valid 'name' field.")
            checks.append({"check": "frontmatter_name", "status": "FAIL"})
        else:
            skill_name = name_match.group(1).strip()
            if len(skill_name) > 64:
                issues.append(f"Frontmatter name exceeds 64 chars ({len(skill_name)}).")
                checks.append({"check": "frontmatter_name_length", "status": "FAIL"})
            else:
                checks.append({"check": "frontmatter_name", "status": "PASS", "name": skill_name})

        desc_match = re.search(r"^description:\s*(?:>-\s*)?(.*)", content, re.MULTILINE)
        if not desc_match:
            issues.append("YAML frontmatter missing 'description' field.")
            checks.append({"check": "frontmatter_description", "status": "FAIL"})
        else:
            checks.append({"check": "frontmatter_description", "status": "PASS"})

        # 3. Check Z-ZOA Scientific Guidelines in doc
        for keyword, label in [
            ("provenance", "rule_1_provenance"),
            ("unit", "rule_2_astropy_units"),
            ("cosmology", "rule_3_cosmology"),
            ("holdout", "rule_4_holdout_protection"),
        ]:
            if keyword.lower() in content.lower():
                checks.append({"check": label, "status": "PASS"})
            else:
                checks.append({"check": label, "status": "WARN", "message": f"Recommended reference to {keyword} missing."})

    # 4. Check scripts
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            text = script.read_text(encoding="utf-8")
            if "output" in text.lower():
                checks.append({"check": f"script_output_handling_{script.name}", "status": "PASS"})
            else:
                issues.append(f"Script {script.name} does not appear to support standard '--output' file redirection.")
                checks.append({"check": f"script_output_handling_{script.name}", "status": "FAIL"})

    overall = "PASS" if len(issues) == 0 else "FAIL"
    print(f"Audit completed for '{skill_path.name}': {overall}")
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print("  All Z-ZOA skill standards verified!")

    return {
        "status": overall,
        "skill_path": str(skill_path),
        "issues": issues,
        "checks": checks,
    }

def main():
    parser = argparse.ArgumentParser(description="Z-ZOA Skill Scaffolder and Auditor")
    parser.add_argument("--output", type=str, default=None, help="Path to write JSON results")

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Scaffold a new Z-ZOA compliant skill")
    p_create.add_argument("--name", type=str, required=True, help="Skill name (lowercase and hyphens, max 64 chars)")
    p_create.add_argument("--description", type=str, required=True, help="Skill description (max 1024 chars)")
    p_create.add_argument("--title", type=str, default=None, help="Human-readable title")
    p_create.add_argument("--install-path", type=str, default=None, help="Target installation directory")
    p_create.add_argument("--dependencies", type=str, default=None, help="Comma-separated required skills")
    p_create.add_argument("--with-script", action="store_true", help="Generate starter CLI script")
    p_create.add_argument("--force", action="store_true", help="Overwrite existing directory")

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit an existing skill against Z-ZOA standards")
    p_audit.add_argument("--skill-path", type=str, required=True, help="Path to skill directory")

    args = parser.parse_args()

    commands = {
        "create": cmd_create,
        "audit": cmd_audit,
    }

    try:
        results = commands[args.subcommand](args)
    except Exception as e:
        print(f"[FAIL] Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Audit artifact written to: {out_path.resolve()}")

if __name__ == "__main__":
    main()
