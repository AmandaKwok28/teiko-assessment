import streamlit as st
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from analysis import (
    get_relative_frequencies,
    get_melanoma_miraclib_pbmc,
    compute_population_statistics,
    get_baseline_melanoma_pbmc,
    count_samples_by_project,
    count_subjects_by_response,
    count_subjects_by_gender,
    avg_b_cells_male_responders
)

st.set_page_config(page_title="Immune Cell Analysis", layout="wide")

st.title("Immune Cell Analysis Dashboard")
st.markdown("Exploratory and statistical analysis of immune populations in clinical trial data.")

conn = sqlite3.connect("data.db")

# create 3 tabs for the different sections of the dashboard
tab1, tab2, tab3 = st.tabs([
    "Relative Frequencies",
    "Response Analysis",
    "Baseline Subset"
])



# tab 1: part2
with tab1:
    st.subheader("Relative Frequency Summary")

    df_summary = get_relative_frequencies(conn)

    col1, col2 = st.columns(2)
    col1.metric("Total Samples", df_summary["sample"].nunique())
    col2.metric("Immune Populations", df_summary["population"].nunique())

    with st.expander("View Full Summary Table"):
        st.dataframe(df_summary, width="stretch")




# tab 2: part3
with tab2:
    st.subheader("Melanoma PBMC – Miraclib Response Comparison")

    filtered_df = get_melanoma_miraclib_pbmc(conn)

    if filtered_df.empty:
        st.warning("No melanoma PBMC miraclib data available.")
    else:

        col1, col2 = st.columns(2)
        col1.metric("Samples", filtered_df["sample"].nunique())
        col2.metric("Subjects", filtered_df["sample"].nunique())

        st.markdown("### Relative Frequency Distribution by Response")

        populations = filtered_df["population"].unique()
        cols = st.columns(4)

        for i, pop in enumerate(populations):
            pop_df = filtered_df[filtered_df["population"] == pop]

            fig, ax = plt.subplots(figsize=(2.2, 2.0))

            sns.boxplot(
                data=pop_df,
                x="response",
                y="percentage",
                ax=ax
            )

            ax.set_title(pop, fontsize=9)
            ax.set_ylabel("%", fontsize=8)
            ax.set_xlabel("")
            ax.tick_params(axis='both', labelsize=7)

            cols[i % 4].pyplot(fig)
            plt.tight_layout()
            plt.close(fig)


        st.markdown("### Statistical Comparison (Mann–Whitney U Test)")

        stats_df = compute_population_statistics(filtered_df)

        st.dataframe(stats_df, width="stretch")

        significant = stats_df[stats_df["significant_(p<0.05)"] == True]

        if not significant.empty:
            st.success(
                f"Significant populations (p < 0.05): "
                f"{', '.join(significant['population'])}"
            )
        else:
            st.info("No statistically significant populations detected.")



# tab 3: part4
with tab3:
    st.subheader("Baseline Subset Analysis")
    st.caption("Melanoma • PBMC • Miraclib • Time = 0")

    baseline_df = get_baseline_melanoma_pbmc(conn)

    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline Samples", len(baseline_df))
    col2.metric("Projects", baseline_df["project"].nunique())
    col3.metric("Subjects", baseline_df["subject"].nunique())

    st.markdown("### Sample Counts by Project")
    st.dataframe(count_samples_by_project(conn), width="stretch")

    st.markdown("### Subjects by Response")
    st.dataframe(count_subjects_by_response(conn), width="stretch")

    st.markdown("### Subjects by Gender")
    st.dataframe(count_subjects_by_gender(conn), width="stretch")

    st.markdown("### Average B Cells (Male Responders)")

    avg_df = avg_b_cells_male_responders(conn)
    value = avg_df.iloc[0]["avg_b_cells"]

    if value is None:
        st.info("No melanoma male responders at baseline.")
    else:
        st.success(f"{value:.2f}")

conn.close()
