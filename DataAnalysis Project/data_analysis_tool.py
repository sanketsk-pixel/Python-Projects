"""
=====================================================================
 DATA ANALYSIS TOOL
 An interactive, menu-driven command-line application for exploring
 any CSV file using Pandas, with visualizations powered by Matplotlib.

 Features:
   - Load any CSV file
   - Dataset overview (shape, dtypes, preview, missing values)
   - Summary statistics (describe)
   - Average / mean of any chosen column
   - Detailed stats for a column (mean, median, std, min, max, sum)
   - Bar chart (grouped averages, or category counts)
   - Scatter plot with an auto-fitted trend line + correlation
   - Correlation heatmap across all numeric columns
   - Automatic plain-English insights & observations

 All charts are saved as PNG files inside a "charts" folder next to
 this script, and also opened in a window if your environment
 supports it.

 Run with:
   python data_analysis_tool.py
=====================================================================
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class DataAnalysisTool:
    def __init__(self):
        self.df = None
        self.filename = None
        self.output_dir = "charts"
        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------------------------------------------
    # Display helpers
    # -----------------------------------------------------------
    def print_header(self, title):
        width = 66
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width)

    def ensure_loaded(self):
        if self.df is None:
            print("No data loaded yet. Use option 1 to load a CSV file first.")
            return False
        return True

    def select_column(self, prompt="Enter column name: ", numeric_only=False):
        cols = list(self.df.select_dtypes(include=np.number).columns) if numeric_only else list(self.df.columns)
        if not cols:
            print("No suitable columns available.")
            return None
        label = "Numeric columns" if numeric_only else "All columns"
        print(f"{label}:", ", ".join(cols))
        col = input(prompt).strip()
        if col not in cols:
            print(f"'{col}' is not a valid choice.")
            return None
        return col

    def save_and_show(self, filename):
        path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        print(f"\nChart saved to: {path}")
        try:
            plt.show()
        except Exception:
            pass
        plt.close()

    # -----------------------------------------------------------
    # Loading & overview
    # -----------------------------------------------------------
    def load_csv(self):
        self.print_header("LOAD CSV FILE")
        path = input("Enter the path to your CSV file: ").strip().strip('"')
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return
        try:
            self.df = pd.read_csv(path)
            self.filename = os.path.basename(path)
            print(f"\nLoaded '{self.filename}' successfully!")
            print(f"Shape: {self.df.shape[0]} rows x {self.df.shape[1]} columns")
        except Exception as e:
            print(f"Error loading file: {e}")

    def show_info(self):
        self.print_header("DATASET OVERVIEW")
        if not self.ensure_loaded():
            return
        print(f"Rows: {self.df.shape[0]}    Columns: {self.df.shape[1]}\n")
        print("Column names and data types:")
        print(self.df.dtypes.to_string())
        print("\nFirst 5 rows:")
        print(self.df.head().to_string())
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            print("\nMissing values per column:")
            print(missing.to_string())
        else:
            print("\nNo missing values detected.")

    def show_summary_stats(self):
        self.print_header("SUMMARY STATISTICS")
        if not self.ensure_loaded():
            return
        numeric_df = self.df.select_dtypes(include=np.number)
        if numeric_df.empty:
            print("No numeric columns found.")
            return
        print(numeric_df.describe().round(3).to_string())

    # -----------------------------------------------------------
    # Basic analysis
    # -----------------------------------------------------------
    def calculate_average(self):
        self.print_header("CALCULATE AVERAGE (MEAN)")
        if not self.ensure_loaded():
            return
        col = self.select_column("Column to average: ", numeric_only=True)
        if col is None:
            return
        print(f"\nAverage of '{col}' = {self.df[col].mean():.4f}")

    def calculate_column_stats(self):
        self.print_header("DETAILED COLUMN STATISTICS")
        if not self.ensure_loaded():
            return
        col = self.select_column("Column to analyze: ", numeric_only=True)
        if col is None:
            return
        s = self.df[col]
        print(f"\nStatistics for '{col}':")
        print(f"  Mean   : {s.mean():.4f}")
        print(f"  Median : {s.median():.4f}")
        print(f"  Std Dev: {s.std():.4f}")
        print(f"  Min    : {s.min():.4f}")
        print(f"  Max    : {s.max():.4f}")
        print(f"  Sum    : {s.sum():.4f}")
        print(f"  Count  : {s.count()}")

    # -----------------------------------------------------------
    # Visualizations
    # -----------------------------------------------------------
    def bar_chart(self):
        self.print_header("BAR CHART")
        if not self.ensure_loaded():
            return
        print("Choose what to plot:")
        print("  1. Average of a numeric column, grouped by a category column")
        print("  2. Count of records per category")
        choice = input("Choose option (1-2): ").strip()

        plt.figure(figsize=(9, 5.5))
        if choice == "1":
            num_col = self.select_column("Numeric column to average: ", numeric_only=True)
            if num_col is None:
                plt.close()
                return
            cat_col = self.select_column("Category column to group by: ")
            if cat_col is None:
                plt.close()
                return
            grouped = self.df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
            if len(grouped) > 20:
                grouped = grouped.head(20)
                print("(Showing top 20 categories)")
            grouped.plot(kind="bar", color="#4C72B0", edgecolor="black")
            plt.ylabel(f"Average {num_col}")
            plt.xlabel(cat_col)
            plt.title(f"Average {num_col} by {cat_col}")
        elif choice == "2":
            cat_col = self.select_column("Categorical column: ")
            if cat_col is None:
                plt.close()
                return
            counts = self.df[cat_col].value_counts()
            if len(counts) > 20:
                counts = counts.head(20)
                print("(Showing top 20 categories)")
            counts.plot(kind="bar", color="#55A868", edgecolor="black")
            plt.ylabel("Count")
            plt.xlabel(cat_col)
            plt.title(f"Record count by {cat_col}")
        else:
            print("Invalid choice.")
            plt.close()
            return

        plt.xticks(rotation=45, ha="right")
        self.save_and_show("bar_chart.png")

    def scatter_plot(self):
        self.print_header("SCATTER PLOT")
        if not self.ensure_loaded():
            return
        x_col = self.select_column("X-axis column: ", numeric_only=True)
        if x_col is None:
            return
        y_col = self.select_column("Y-axis column: ", numeric_only=True)
        if y_col is None:
            return

        plt.figure(figsize=(8, 6))
        plt.scatter(self.df[x_col], self.df[y_col], alpha=0.6,
                    color="#C44E52", edgecolor="white", linewidth=0.4)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{y_col} vs {x_col}")

        valid = self.df[[x_col, y_col]].dropna()
        if len(valid) >= 2:
            z = np.polyfit(valid[x_col], valid[y_col], 1)
            p = np.poly1d(z)
            x_sorted = np.sort(valid[x_col])
            plt.plot(x_sorted, p(x_sorted), color="black", linestyle="--",
                      linewidth=1.5, label="Trend line")
            plt.legend()
            corr = valid[x_col].corr(valid[y_col])
            print(f"\nCorrelation between '{x_col}' and '{y_col}': {corr:.4f}")

        self.save_and_show("scatter_plot.png")

    def heatmap(self):
        self.print_header("CORRELATION HEATMAP")
        if not self.ensure_loaded():
            return
        numeric_df = self.df.select_dtypes(include=np.number)
        if numeric_df.shape[1] < 2:
            print("Need at least 2 numeric columns for a correlation heatmap.")
            return
        corr = numeric_df.corr()
        n = len(corr.columns)

        fig, ax = plt.subplots(figsize=(max(6, n * 0.9), max(5, n * 0.8)))
        im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)

        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticklabels(corr.columns)

        for i in range(n):
            for j in range(n):
                value = corr.values[i, j]
                color = "white" if abs(value) > 0.5 else "black"
                ax.text(j, i, f"{value:.2f}", ha="center", va="center",
                        color=color, fontsize=8)

        fig.colorbar(im, ax=ax, label="Correlation coefficient")
        ax.set_title("Correlation Heatmap of Numeric Columns")
        self.save_and_show("correlation_heatmap.png")

    # -----------------------------------------------------------
    # Automatic insights
    # -----------------------------------------------------------
    def auto_insights(self):
        self.print_header("AUTOMATIC INSIGHTS")
        if not self.ensure_loaded():
            return
        numeric_df = self.df.select_dtypes(include=np.number)
        if numeric_df.empty:
            print("No numeric columns to analyze.")
            return

        print(f"Dataset: {self.df.shape[0]} rows, {self.df.shape[1]} columns "
              f"({numeric_df.shape[1]} numeric).\n")

        for col in numeric_df.columns:
            s = numeric_df[col].dropna()
            if s.empty:
                continue
            print(f"- '{col}': mean={s.mean():.2f}, median={s.median():.2f}, "
                  f"std={s.std():.2f}, range=({s.min():.2f} to {s.max():.2f})")
            skew = s.skew()
            if abs(skew) > 1:
                direction = "right (positively)" if skew > 0 else "left (negatively)"
                print(f"    -> Distribution is notably skewed {direction} (skew={skew:.2f}).")

        if numeric_df.shape[1] >= 2:
            corr = numeric_df.corr()
            cols = corr.columns
            pairs = []
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    pairs.append((cols[i], cols[j], corr.iloc[i, j]))
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            print("\nStrongest relationships between numeric columns:")
            for a, b, c in pairs[:3]:
                strength = "strong" if abs(c) > 0.7 else "moderate" if abs(c) > 0.4 else "weak"
                direction = "positive" if c > 0 else "negative"
                print(f"  - {a} & {b}: r={c:.2f} ({strength} {direction} relationship)")

        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            print("\nMissing data found in:")
            for col, n_missing in missing.items():
                pct = 100 * n_missing / len(self.df)
                print(f"  - {col}: {n_missing} missing ({pct:.1f}%)")

    # -----------------------------------------------------------
    # Main menu loop
    # -----------------------------------------------------------
    def run(self):
        self.print_header("WELCOME TO THE DATA ANALYSIS TOOL")
        print("Built with Python + Pandas + Matplotlib".center(66))

        menu = {
            "1": ("Load a CSV file", self.load_csv),
            "2": ("Dataset overview (shape, types, preview, missing values)", self.show_info),
            "3": ("Summary statistics (describe)", self.show_summary_stats),
            "4": ("Calculate average (mean) of a column", self.calculate_average),
            "5": ("Detailed statistics for a column", self.calculate_column_stats),
            "6": ("Bar chart", self.bar_chart),
            "7": ("Scatter plot (with trend line + correlation)", self.scatter_plot),
            "8": ("Correlation heatmap", self.heatmap),
            "9": ("Automatic insights & observations", self.auto_insights),
            "0": ("Exit", None),
        }

        while True:
            self.print_header("MAIN MENU")
            for key in sorted(menu.keys(), key=int):
                print(f"  {key}. {menu[key][0]}")
            choice = input("\nEnter your choice: ").strip()

            if choice == "0":
                print("\nThanks for using the Data Analysis Tool. Goodbye!")
                break
            elif choice in menu:
                try:
                    menu[choice][1]()
                except Exception as e:
                    print(f"\nAn unexpected error occurred: {e}")
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice. Please pick a number from the menu.")


if __name__ == "__main__":
    try:
        DataAnalysisTool().run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)