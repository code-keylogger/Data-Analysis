from proof_data_analysis.plots import plot_edits, plot_jumps, plot_letter_count
from proof_data_analysis.utils import load_df


class TestPlots:
    def test_plots(self):
        """Just test that the function runs without error"""
        df = load_df("tests/example.json")
        plot_edits(df)
        plot_letter_count(df)
        plot_jumps(df)
