# Figure pipeline

`data/figure_data.json` currently holds PROJECTED placeholder data. It was produced by
`generate_projected_data.py` and is not a measurement.

1. Replace `data/figure_data.json` with measured results, keeping the same schema
   (see `generate_projected_data.py` for the structure of every field).
2. Run `python make_figures.py` to regenerate the vector PDFs in `../figures/`.
3. Run `python derived_stats.py` to print the statistics quoted in `main.tex`
   (update the matching `%reference` lines).

Requirements: `pip install numpy scipy matplotlib`.
