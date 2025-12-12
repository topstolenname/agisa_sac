# ⚡ QUICK START - 5 Commands to Completion

```bash
# 1. Navigate
cd "C:\New folder\agisa_sac"

# 2. Create figures (run reconciliation script)
bash docs/figs/reconcile_figures.sh

# 3. Organize alt-text files
mv fig*.md docs/figs/alt/

# 4. Edit mkdocs.yml
# Add these 3 lines to Gallery section:
#   - "Figure 0 – Layer Stack": gallery/figure0.md
#   - "Figure Φ – Integration": gallery/figure_phi.md
#   - "Figure Code – Mapping": gallery/figure_code.md

# 5. Commit and push
git add -A
git commit -m "docs: Complete figure set with Layer Stack, Φ Integration, and Code Mapping"
git push origin main
```

## ✅ What You Get

**Before**: 7 figures, 3 missing  
**After**: 10 figures, complete package

## 📦 Files Created

Claude just created for you:
- ✅ 3 alt-text files (docs/figs/alt/)
- ✅ 3 gallery pages (docs/gallery/)
- ✅ 1 alt directory (docs/figs/alt/)
- ✅ This guide

Your script will create:
- ✅ 3 figure sources (docs/figs/src/)
- ✅ 3 rendered SVGs (docs/figs/svg/)
- ✅ Status report (docs/figs/CURRENT_STATUS.md)

## ⏱️ Time Budget

- Step 1: 10 seconds
- Step 2: 2-5 minutes (depending on tool installation)
- Step 3: 30 seconds
- Step 4: 2 minutes
- Step 5: 1 minute

**Total**: ~10 minutes if tools are installed, ~20 minutes if you need to install rendering tools

## 🎯 Success = 

```bash
git log -1 --oneline
# Should show: "docs: Complete figure set..."

ls docs/figs/src/*.mmd docs/figs/src/*.dot | wc -l
# Should show: 6 (3 existing + 3 new mermaid/dot files)

ls docs/figs/alt/*.md | wc -l  
# Should show: 10 (all alt-text files)
```

## 🚀 Execute Now

See FINAL_COMPLETION_GUIDE.md for detailed instructions.

**Don't overthink it - just run the 5 commands above!**
