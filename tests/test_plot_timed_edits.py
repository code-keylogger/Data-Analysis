from proof_data_analysis.plots import plot_edits_over_time, plot_letter_count
from proof_data_analysis.utils import load_df


class TestPlotTimedEdits:
    def test_plot_timed_edits(self):
        """Just test that the function runs without error"""
        df = load_df("tests/example.json")
        plot_edits_over_time(df)
        plot_letter_count(df)
