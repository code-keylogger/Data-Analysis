from proof_data_analysis.plots import plot_edits_over_time, plot_letter_count, plot_jumps
from proof_data_analysis.utils import load_df


class TestPlots:
    def test_plots(self):
        """Just test that the function runs without error"""
        df = load_df("tests/example.json")
        plot_edits_over_time(df)
        plot_letter_count(df)
        plot_jumps(df)
