# ================================================= Libraries =========================================================


import pandas as pd
import plotly.express as px

from datetime import datetime

from iteration3.models import DiaryEntries


# ================================================= Metrics Views =====================================================


# Chart layout update view.
def figure_update(fig1, fig2, fig3, fig4):
    # Figure 1.
    fig1.update_layout(title={'xanchor': 'center', 'x': 0.5, 'font_size': 16},
                       paper_bgcolor="rgba(0,0,0,0)")
    fig1.update_yaxes(showticklabels=True, matches=None)
    fig1.update_traces(marker=dict(size=8,
                                   line=dict(width=2,
                                             color='DarkSlateGrey')),
                       selector=dict(mode='markers'))

    # Figure 2.
    fig2.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                       paper_bgcolor="rgba(0,0,0,0)")
    fig2.update_yaxes(showticklabels=True, matches=None)
    fig2.update_traces(marker=dict(size=8,
                                   line=dict(width=2,
                                             color='DarkSlateGrey')),
                       selector=dict(mode='markers'))

    # Figure 3.
    fig3.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                       paper_bgcolor="rgba(0,0,0,0)")
    fig3.update_yaxes(showticklabels=True, matches=None)
    fig3.update_traces(marker=dict(size=8,
                                   line=dict(width=2,
                                             color='DarkSlateGrey')),
                       selector=dict(mode='markers'))

    # Figure 4.
    fig4.update_layout(title={'xanchor': 'center', 'x': 0.5, 'font_size': 16},
                       paper_bgcolor="rgba(0,0,0,0)")
    fig4.update_yaxes(showticklabels=True, matches=None)
    fig4.update_traces(marker=dict(size=8,
                                   line=dict(width=2,
                                             color='DarkSlateGrey')),
                       selector=dict(mode='markers'))
    return fig1, fig2, fig3, fig4


# Generating the charts if the entries exist.
def entries_function(request):
    # Entries retrieval
    entries = DiaryEntries.objects.filter(user_id=request.session['_auth_user_id']).all().order_by('date', 'time')

    # Dataframe generation.
    date = [datetime.combine(c.date, c.time) for c in entries]
    bsl = [c.blood_sugar_level for c in entries]
    carbs = [c.carbohydrates for c in entries]
    isl = [round(c.insulin) for c in entries]
    df = pd.DataFrame({'Date': date, 'Blood Sugar (mmol/L)': bsl, 'Insulin (units)': isl, 'Carbs (g)': carbs})

    # Figure plotting.
    fig1 = px.scatter(
        df,
        x='Date',
        y='Blood Sugar (mmol/L)',
        title='Blood Sugar Levels',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )
    # Figure plotting.
    fig2 = px.scatter(
        df,
        x='Date',
        y='Carbs (g)',
        title='Carbohydrates (g)',
        labels={'x': 'Date', 'y': 'Carbs (g)'}
    )
    # Figure plotting.
    fig3 = px.scatter(
        df,
        x='Date',
        y='Insulin (units)',
        title='Insulin',
        labels={'x': 'Date', 'y': 'Insulin (units)'}
    )

    # Melting to generate Figure 4 (faceted chart to be mailed)
    df_melt = df.melt(id_vars='Date', value_vars=['Blood Sugar (mmol/L)', 'Insulin (units)', 'Carbs (g)'])
    df_melt = df_melt.rename(columns={'variable': 'Legend'})

    # Figure plotting.
    fig4 = px.scatter(
        df_melt,
        x='Date',
        y='value',
        facet_col='Legend',
        facet_col_wrap=3,
        color='Legend',
        title='Metrics Chart',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )

    # Statistics regarding each metric.
    bsl_list = df['Blood Sugar (mmol/L)'].min(), df['Blood Sugar (mmol/L)'].max(), df['Blood Sugar (mmol/L)'].mean()
    bsl_list = [round(v, 1) for v in bsl_list]
    carbs_list = df['Carbs (g)'].min(), df['Carbs (g)'].max(), df['Carbs (g)'].mean()
    carbs_list = [round(v, 2) for v in carbs_list]
    isl_list = df['Insulin (units)'].min(), df['Insulin (units)'].max(), df['Insulin (units)'].mean()
    isl_list = [round(v) for v in isl_list]

    # Update the layouts of the charts.
    fig1, fig2, fig3, fig4 = figure_update(fig1, fig2, fig3, fig4)

    # Write the faceted chart to html.
    fig4.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))
    return fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4


# Generating the charts if the entries do not exist.
def no_entries_function(request):
    # Axes.
    x = y = [0]
    bsl_list = carbs_list = isl_list = [0, 0, 0]

    # Figure plotting.
    fig4 = px.scatter(
        x=x,
        y=y,
        title='Metrics Chart',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )

    # Figure plotting.
    fig1 = px.scatter(
        x=x,
        y=y,
        title='Blood Sugar Levels',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )

    # Figure plotting.
    fig2 = px.scatter(
        x=x,
        y=y,
        title='Carbohydrates (g)',
        labels={'x': 'Date', 'y': 'Carbs (g)'}
    )

    # Figure plotting.
    fig3 = px.scatter(
        x=x,
        y=y,
        title='Insulin',
        labels={'x': 'Date', 'y': 'Insulin (units)'}
    )

    # Update the layouts of the charts.
    fig1, fig2, fig3, fig4 = figure_update(fig1, fig2, fig3, fig4)

    # Write the faceted chart to a html file.
    fig4.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))
    return fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4


# ================================================= Metrics Views ===================================================
