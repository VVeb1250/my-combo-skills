import subprocess, sys, re, json
repo, pin = sys.argv[1], sys.argv[2]
def git(*a):
    return subprocess.run(["git","-C",repo,*a],capture_output=True,text=True,encoding="utf-8").stdout
names = [l.split("\t") for l in git("diff","--name-status","-M",pin,"origin/HEAD","--","skills/").splitlines()]
out = {"desc_only":[], "body_small":[], "body_large":[], "deleted":[], "renamed":[], "added":[]}
for st,*paths in names:
    p = paths[-1]
    if st.startswith("D"): out["deleted"].append(p); continue
    if st.startswith("A"): out["added"].append(p); continue
    if st.startswith("R"): out["renamed"].append(paths); continue
    d = git("diff","-U0",pin,"origin/HEAD","--",p).splitlines()
    ch = [l for l in d if l[:1] in "+-" and not l.startswith(("+++","---"))]
    body = [l for l in ch if not re.match(r"^[+-](description|name|version|origin|tools|model):",l) and not re.match(r"^[+-]\s{2,}\S",l) or False]
    # crude: frontmatter lines = those before 2nd '---'; compute via hunk header line numbers
    hunks=[(int(m.group(1)),) for l in d if (m:=re.match(r"@@ -(\d+)",l))]
    fm_only = all(h[0] <= 12 for h in hunks) and len(ch)<=8
    n=len(ch)
    if fm_only: out["desc_only"].append((p,n))
    elif n<=20: out["body_small"].append((p,n))
    else: out["body_large"].append((p,n))
for k,v in out.items(): print(k,len(v))
print("\nLARGE:"); [print(" ",p,n) for p,n in sorted(out["body_large"],key=lambda x:-x[1])]
print("\nSMALL:"); [print(" ",p,n) for p,n in out["body_small"]]
print("\nDELETED/RENAMED:",out["deleted"],out["renamed"])
