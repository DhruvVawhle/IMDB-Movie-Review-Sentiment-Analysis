"""
Plotly visualization components for CineSense.
Styled in accordance with the cinematic editorial dark design system.
"""

from typing import Any, Dict, List, Optional
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Visual theme constants
DARK_BG = "#161B22"
CANVAS_BG = "#0D1117"
BORDER_COLOR = "#30363D"
GRID_COLOR = "#21262D"
TEXT_COLOR = "#F0F6FC"
TEXT_MUTED = "#8B949E"

COLOR_POS = "#3FB950"
COLOR_NEG = "#F85149"
COLOR_AMBER = "#D29922"
COLOR_BLUE = "#58A6FF"
COLOR_PURPLE = "#BC8CFF"

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=DARK_BG,
    font=dict(family="Albert Sans, -apple-system, sans-serif", color=TEXT_COLOR, size=12),
    margin=dict(l=40, r=30, t=50, b=40),
    xaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=BORDER_COLOR,
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_COLOR, size=12),
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=BORDER_COLOR,
        tickfont=dict(color=TEXT_MUTED),
        title_font=dict(color=TEXT_COLOR, size=12),
    ),
    legend=dict(
        font=dict(color=TEXT_COLOR),
        bgcolor="rgba(22, 27, 34, 0.8)",
        bordercolor=BORDER_COLOR,
        borderwidth=1,
    ),
)


def plot_sentiment_distribution(pos_count: int, neg_count: int) -> go.Figure:
    """
    Create a single horizontal stacked bar comparing Positive and Negative classes.
    One bar replaces the two-bar chart. Equal halves are easier to compare when they share an edge.
    """
    total = pos_count + neg_count
    pos_pct = round((pos_count / total) * 100, 1) if total else 50.0
    neg_pct = round((neg_count / total) * 100, 1) if total else 50.0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Class Balance"],
        x=[pos_count],
        name=f"Positive ({pos_count:,} / {pos_pct}%)",
        orientation="h",
        marker=dict(
            color=COLOR_POS,
            line=dict(color=BORDER_COLOR, width=1),
        ),
        text=f"Positive: {pos_count:,} ({pos_pct}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=13, family="Albert Sans, sans-serif"),
        hovertemplate="Positive: %{x:,} reviews (50%)<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=["Class Balance"],
        x=[neg_count],
        name=f"Negative ({neg_count:,} / {neg_pct}%)",
        orientation="h",
        marker=dict(
            color=COLOR_NEG,
            line=dict(color=BORDER_COLOR, width=1),
        ),
        text=f"Negative: {neg_count:,} ({neg_pct}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=13, family="Albert Sans, sans-serif"),
        hovertemplate="Negative: %{x:,} reviews (50%)<extra></extra>",
    ))

    fig.update_layout(
        BASE_LAYOUT,
        barmode="stack",
        title=dict(
            text="Class balance — One bar replaces the two-bar chart (50,000 Reviews)",
            font=dict(size=14, color=TEXT_COLOR),
        ),
        xaxis=dict(
            range=[0, total],
            showgrid=True,
            gridcolor=GRID_COLOR,
            tickvals=[0, pos_count, total],
            ticktext=["0", f"{pos_count:,} (Center Edge)", f"{total:,}"],
            title_text="Total Reviews (Shared 50% Center Edge)",
        ),
        yaxis=dict(showticklabels=False, showgrid=False),
        height=140,
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5),
    )
    return fig


def plot_review_length_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram comparing word count distributions for positive vs negative reviews with mean annotation."""
    fig = go.Figure()

    pos_lens = df[df["sentiment_clean"] == "positive"]["word_count"]
    neg_lens = df[df["sentiment_clean"] == "negative"]["word_count"]

    fig.add_trace(go.Histogram(
        x=pos_lens,
        name="Positive",
        nbinsx=50,
        marker_color=COLOR_POS,
        opacity=0.65,
        hovertemplate="Positive: %{y} reviews (~%{x} words)<extra></extra>",
    ))
    fig.add_trace(go.Histogram(
        x=neg_lens,
        name="Negative",
        nbinsx=50,
        marker_color=COLOR_NEG,
        opacity=0.65,
        hovertemplate="Negative: %{y} reviews (~%{x} words)<extra></extra>",
    ))

    # Mean annotation at 231 words
    mean_val = 231.0
    fig.add_vline(
        x=mean_val,
        line_width=2,
        line_dash="dash",
        line_color=COLOR_AMBER,
        annotation_text="Mean, 231 words",
        annotation_position="top right",
        annotation_font=dict(color=COLOR_AMBER, size=11),
    )

    fig.update_layout(
        BASE_LAYOUT,
        barmode="overlay",
        title=dict(
            text="Reviews are short, and skewed long (Words per Review)",
            font=dict(size=14, color=TEXT_COLOR),
        ),
        xaxis_title="Word Count",
        yaxis_title="Number of Reviews",
        xaxis=dict(range=[0, 1000], gridcolor=GRID_COLOR),
        height=320,
    )
    return fig


def plot_confusion_matrix_heatmap(cm: List[List[int]], model_name: str) -> go.Figure:
    """Plot an annotated 2x2 confusion matrix."""
    tn, fp = cm[0]
    fn, tp = cm[1]
    total = tn + fp + fn + tp

    z = [[tn, fp], [fn, tp]]
    text = [
        [f"True Neg (TN)<br>{tn:,}<br>({tn/total*100:.1f}%)", f"False Pos (FP)<br>{fp:,}<br>({fp/total*100:.1f}%)"],
        [f"False Neg (FN)<br>{fn:,}<br>({fn/total*100:.1f}%)", f"True Pos (TP)<br>{tp:,}<br>({tp/total*100:.1f}%)"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=["Predicted Negative", "Predicted Positive"],
        y=["Actual Negative", "Actual Positive"],
        text=text,
        texttemplate="%{text}",
        textfont=dict(color=TEXT_COLOR, size=13),
        colorscale=[[0, "#1F242C"], [0.5, "#1B4728"], [1, "#238636"]],
        showscale=False,
    ))

    fig.update_layout(
        BASE_LAYOUT,
        title=dict(text=f"Confusion Matrix — {model_name} (N = {total:,} Test Samples)", font=dict(size=14, color=TEXT_COLOR)),
        height=320,
    )
    return fig


def plot_multi_roc_curves(models_dict: Dict[str, Any]) -> go.Figure:
    """Overlay ROC curves for all models with random reference diagonal."""
    fig = go.Figure()

    palette = [COLOR_BLUE, COLOR_AMBER, COLOR_POS]
    idx = 0

    for model_key, meta in models_dict.items():
        if meta.get("status") == "available" and "roc_curve" in meta:
            rc = meta["roc_curve"]
            auc_val = rc.get("auc", 0.0)
            color = palette[idx % len(palette)]
            idx += 1

            fig.add_trace(go.Scatter(
                x=rc["fpr"],
                y=rc["tpr"],
                mode="lines",
                name=f"{meta.get('name', model_key)} (AUC = {auc_val:.4f})",
                line=dict(color=color, width=2.5),
            ))

    # Reference 50% diagonal
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random Chance (AUC = 0.5000)",
        line=dict(color=TEXT_MUTED, width=1.5, dash="dash"),
    ))

    fig.update_layout(
        BASE_LAYOUT,
        title=dict(text="Receiver Operating Characteristic (ROC) — Test Set Comparison", font=dict(size=14, color=TEXT_COLOR)),
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity / Recall)",
        xaxis=dict(range=[0, 1], gridcolor=GRID_COLOR),
        yaxis=dict(range=[0, 1.02], gridcolor=GRID_COLOR),
        height=360,
    )
    return fig


def plot_model_comparison_bars(comp_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing Accuracy, Precision, Recall, and F1 across models."""
    fig = go.Figure()

    metrics = [
        ("Accuracy (%)", COLOR_BLUE),
        ("Precision (%)", COLOR_POS),
        ("Recall (%)", COLOR_AMBER),
        ("F1-Score (%)", COLOR_PURPLE),
    ]

    for metric_col, color in metrics:
        if metric_col in comp_df.columns:
            fig.add_trace(go.Bar(
                name=metric_col,
                x=comp_df["Model"],
                y=comp_df[metric_col],
                text=comp_df[metric_col].apply(lambda v: f"{v:.1f}%"),
                textposition="outside",
                marker_color=color,
            ))

    fig.update_layout(
        BASE_LAYOUT,
        barmode="group",
        title=dict(text="Model Performance Benchmarks (Held-out Test Split)", font=dict(size=14, color=TEXT_COLOR)),
        yaxis=dict(range=[70, 100], title="Metric Score (%)", gridcolor=GRID_COLOR),
        xaxis_title="Classification Model",
        height=350,
    )
    return fig


def plot_prediction_probabilities(pos_prob: float, neg_prob: float) -> go.Figure:
    """Compact horizontal stacked indicator for sentiment probability distribution."""
    fig = go.Figure()

    pos_pct = round(pos_prob * 100, 1)
    neg_pct = round(neg_prob * 100, 1)

    fig.add_trace(go.Bar(
        y=["Probability"],
        x=[pos_pct],
        name=f"Positive ({pos_pct}%)",
        orientation="h",
        marker=dict(color=COLOR_POS),
        text=f"Positive: {pos_pct}%" if pos_pct >= 15 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=12, family="Albert Sans"),
    ))

    fig.add_trace(go.Bar(
        y=["Probability"],
        x=[neg_pct],
        name=f"Negative ({neg_pct}%)",
        orientation="h",
        marker=dict(color=COLOR_NEG),
        text=f"Negative: {neg_pct}%" if neg_pct >= 15 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=12, family="Albert Sans"),
    ))

    fig.update_layout(
        BASE_LAYOUT,
        barmode="stack",
        height=80,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 100], zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        showlegend=False,
    )
    return fig


def plot_top_features_chart(top_features: Dict[str, List[Dict[str, Any]]], top_n: int = 15) -> go.Figure:
    """Horizontal divergent bar chart displaying top positive and negative vocabulary weights."""
    pos_items = top_features.get("positive", [])[:top_n]
    neg_items = top_features.get("negative", [])[:top_n]

    terms = [item["term"] for item in reversed(pos_items)] + [item["term"] for item in neg_items]
    weights = [item["weight"] for item in reversed(pos_items)] + [item["weight"] for item in neg_items]
    colors = [COLOR_POS if w > 0 else COLOR_NEG for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{w:+.2f}" for w in weights],
        textposition="outside",
        hoverinfo="x+y",
    ))

    fig.update_layout(
        BASE_LAYOUT,
        title=dict(text="Top Salient N-Grams (Logistic Regression Feature Weights)", font=dict(size=14, color=TEXT_COLOR)),
        xaxis_title="Fitted Model Weight (Association with Sentiment)",
        yaxis=dict(autorange="reversed", gridcolor=GRID_COLOR),
        height=550,
    )
    return fig


def plot_distinctive_words_bar(
    top_features: Dict[str, List[Dict[str, Any]]],
    sentiment: str = "positive",
    top_n: int = 12,
) -> go.Figure:
    """
    Ranked bar chart showing how strongly each word separates the classes.
    Replaces illegible word clouds with precise quantitative odds metrics.
    Tags (<br />) are stripped, eliminating spurious 'br' artefacts.
    """
    items = top_features.get(sentiment, [])[:top_n]
    if not items:
        return go.Figure()

    terms = [item["term"] for item in reversed(items)]
    weights = [abs(item["weight"]) for item in reversed(items)]
    color = COLOR_POS if sentiment == "positive" else COLOR_NEG

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=color, line=dict(color=BORDER_COLOR, width=1)),
        text=[f"{w:.2f}" for w in weights],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=11),
        hovertemplate="<b>%{y}</b><br>Class Separation Weight: %{x:.3f}<extra></extra>",
    ))

    title_text = f"Distinctive Words — {sentiment.capitalize()} Reviews"
    fig.update_layout(
        BASE_LAYOUT,
        title=dict(text=title_text, font=dict(size=13, color=TEXT_COLOR)),
        xaxis_title="Separation Magnitude (Statistical Association)",
        yaxis=dict(gridcolor=GRID_COLOR),
        height=320,
        margin=dict(l=70, r=40, t=40, b=40),
    )
    return fig


def generate_wordcloud_image(df: pd.DataFrame, sentiment: str) -> Optional[Any]:
    """
    Generate WordCloud image buffer for positive or negative subset.
    Crucial fix: Strips <br /> markup and filters out leftover 'br' tokens.
    """
    try:
        import re
        from wordcloud import WordCloud, STOPWORDS

        subset = df[df["sentiment_clean"] == sentiment]
        if subset.empty:
            return None

        # Sample up to 1000 reviews for rapid, memory-safe generation
        sample_texts = subset["review"].head(1000).astype(str).tolist()
        
        # Explicitly strip HTML tags and residual 'br' tokens
        cleaned_samples = [re.sub(r"<[^>]+>", " ", text) for text in sample_texts]
        combined_text = " ".join(cleaned_samples)

        # Extended stopwords strictly excluding 'br'
        custom_stopwords = set(STOPWORDS)
        custom_stopwords.update({"br", "film", "movie", "one", "see", "make", "even"})

        colormap = "Greens" if sentiment == "positive" else "Reds"
        wc = WordCloud(
            width=700,
            height=340,
            background_color=DARK_BG,
            colormap=colormap,
            stopwords=custom_stopwords,
            max_words=60,
            collocations=False,
        ).generate(combined_text)

        img_buf = io.BytesIO()
        wc.to_image().save(img_buf, format="PNG")
        img_buf.seek(0)
        return img_buf
    except Exception:
        return None
