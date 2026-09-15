"""Pre-submit audit against Cursor's marketplace checklist.

Every marketplace update is re-reviewed, so run this before each submission:

    python3 scripts/validate.py .

It checks the manifest shape, that the name matches Cursor's naming rules, that every
declared path is relative and exists, that each ${VAR} used in mcp.json is declared in
the manifest, that every skill has parseable frontmatter whose name matches its
directory, and that no token or key has been committed.
"""
import json, os, re, sys

D = sys.argv[1] if len(sys.argv) > 1 else "."
ok, fail = [], []
def check(cond, msg):
    (ok if cond else fail).append(msg)

# --- manifest ---
mpath = os.path.join(D, ".cursor-plugin", "plugin.json")
check(os.path.isfile(mpath), "manifest at .cursor-plugin/plugin.json")
m = json.load(open(mpath))
check(json.dumps(m) is not None, "manifest is valid JSON")

name = m.get("name", "")
check(bool(re.fullmatch(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?", name)),
      f"name '{name}' is lowercase kebab-case, starts/ends alphanumeric")
check("--" not in name and ".." not in name, "no consecutive hyphens or dots in name")
check(1 <= len(name) <= 64, "name length 1-64")
check(bool(m.get("description")), "description present")

# --- relative, existing paths ---
for key in ("logo", "skills", "mcpServers"):
    v = m.get(key)
    if not isinstance(v, str):
        continue
    check(not v.startswith("/") and ".." not in v, f"{key} path '{v}' is relative, no ..")
    check(os.path.exists(os.path.join(D, v)), f"{key} path '{v}' exists")

# --- mcp.json ---
mcp = json.load(open(os.path.join(D, m.get("mcpServers", "mcp.json"))))
servers = mcp.get("mcpServers") or {}
check(len(servers) >= 1, f"mcp.json declares {len(servers)} server(s)")
for sname, s in servers.items():
    check(s.get("type") in ("streamable-http", "sse", None),
          f"{sname}: type '{s.get('type')}' is a valid remote transport")
    check(str(s.get("url", "")).startswith("https://"), f"{sname}: url is https")

# --- every ${VAR} declared ---
declared = set((m.get("variables") or {}).get("properties", {}).keys())
used = set(re.findall(r"\$\{([A-Za-z0-9_]+)\}", json.dumps(mcp)))
check(used <= declared, f"every ${{VAR}} used {sorted(used)} is declared {sorted(declared)}")
check(bool(used), "mcp.json uses a variable rather than a literal token")

# --- skills ---
sdir = os.path.join(D, m.get("skills", "skills"))
skills = sorted(d for d in os.listdir(sdir) if os.path.isdir(os.path.join(sdir, d)))
check(len(skills) >= 3, f"{len(skills)} skills present")
for sk in skills:
    f = os.path.join(sdir, sk, "SKILL.md")
    check(os.path.isfile(f), f"{sk}/SKILL.md exists")
    txt = open(f).read()
    fm = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    check(bool(fm), f"{sk}: frontmatter block parses")
    if fm:
        body = fm.group(1)
        nm = re.search(r"^name:\s*(\S+)", body, re.M)
        check(bool(nm), f"{sk}: frontmatter has name")
        check(nm and nm.group(1) == sk, f"{sk}: frontmatter name matches directory")
        check(bool(re.search(r"^description:\s*\S", body, re.M)), f"{sk}: frontmatter has description")

# --- no secrets ---
leak = []
for root, _, files in os.walk(D):
    if ".git" in root: continue
    for fn in files:
        p = os.path.join(root, fn)
        try: t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception: continue
        # Patterns are assembled at runtime so this file does not itself contain a
        # literal that its own scan would flag.
        pats = ["fc_" + "live_" + "[A-Za-z0-9]{16,}",
                "eyJ" + "hbGciOi",
                "-----" + "BEGIN [A-Z]"]
        if re.search("|".join(pats), t):
            leak.append(os.path.relpath(p, D))
check(not leak, f"no secrets committed{' — FOUND: '+', '.join(leak) if leak else ''}")

# --- README ---
r = os.path.join(D, "README.md")
check(os.path.isfile(r), "README.md exists")
rt = open(r).read()
check("FIELDCAMP_API_TOKEN" in rt, "README names the required variable")
check(len(rt) > 800, "README is substantive")
check(os.path.isfile(os.path.join(D, "LICENSE")), "LICENSE present")

print("PASS %d" % len(ok))
for m_ in ok: print("  ✅", m_)
if fail:
    print("\nFAIL %d" % len(fail))
    for m_ in fail: print("  ❌", m_)
sys.exit(1 if fail else 0)
