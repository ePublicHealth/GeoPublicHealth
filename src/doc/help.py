# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2014-08-20
        copyright            : (C) 2014 by Etienne Trimaille, (C) 2017 by
        Rachel Gorée et Christophe Révillion
        email                : etienne@trimaille.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from os.path import dirname, abspath, join
from geopublichealth.src.core.tools import tr


PATH = dirname(abspath(__file__))


def html_table(title, intro, inputs, outputs, more):
    html_string = (
        ""
        "<html>"
        "<head>"
        '<style type="text/css">'
        "body {"
        "font-family: Ubuntu,Verdana,Arial,helvetica;"
        "margin:0px;"
        "padding:0px;"
        "background-color:#B7B7B7;"
        "}"
        "table {"
        "padding: 0;"
        "width:100%%;"
        "}"
        "tr:nth-child(even) {"
        "background-color:#DBDBDB;"
        "}"
        "tr:nth-child(odd) {"
        "background-color:#CACACA;"
        "}"
        "caption {"
        "background-color:#129300;"
        "font-size:20;"
        "color:#FFFFDC;"
        "font-style:bold;"
        "padding:5px;"
        "}"
        ".more{"
        "list-style-type: none;"
        "}"
        "</style>"
        "</head>"
        "<body><table>"
        "<caption>%s</caption>"
        "<tr>"
        "<td>%s</td>"
        "</tr>"
        "<tr>"
        "<td>"
        "<strong>Input</strong>"
        "<ul>" % (title, intro)
    )

    for item in inputs:
        html_string += "<li>%s</li>" % item

    html_string += "</ul></td></tr><tr><td><strong>Output</strong><ul>"

    for item in outputs:
        html_string += "<li>%s</li>" % item

    html_string += "</ul></td></tr>"
    if len(more) > 0:
        html_string += "<tr><td><strong>More</strong><ul>"

        for item in more:
            html_string += '<li class="more">%s</li>' % item

        html_string += "</ul></td></tr>"

    html_string += "</table></body></html>"

    return html_string


def picture(filename):
    return "<img src='file:%s' />" % (join(PATH, filename))


def help_open_shapefile():
    title = tr("Import shapefile")
    intro = tr("Import a shapefile into QGIS.")
    inputs = [tr("Shapefile")]
    outputs = [tr("New layer")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_open_raster():
    title = tr("Import raster")
    intro = tr("Import a raster into QGIS.")
    inputs = [tr("Raster file")]
    outputs = [tr("New layer")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_open_table():
    title = tr("Import table")
    intro = tr("XLS or DBF format.")
    inputs = [tr("Table file")]
    outputs = [tr("New table")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_open_csv():
    title = tr("Import CSV table")
    intro = tr("CSV format without geometry.")
    inputs = [tr("CSV file")]
    outputs = [tr("New table")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_open_xy():
    title = tr("Import CSV table")
    intro = tr("CSV format with geometry.")
    inputs = [tr("CSV file")]
    outputs = [tr("New layer")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_density():
    title = tr("Density")
    intro = tr("Compute density")
    inputs = [
        tr("Point layer : disease"),
        tr("Polygon layer : administrative boundary"),
        tr("Case field"),
        tr("Ratio"),
        tr("New column"),
    ]
    outputs = [tr("New polygon layer with the density")]
    more = [
        tr(
            "This algorithm will count the number of points inside each "
            "polygons and run a formula to get the density."
        ),
        tr("number of cases / area * ratio"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_density_point():
    title = tr("Density with case layer")
    intro = tr("Compute density")
    inputs = [
        tr("Case layer"),
        tr("Polygon layer : administrative boundary with two fields pop and case"),
        tr("Ratio"),
        tr("New column"),
    ]
    outputs = [tr("New polygon layer with the density")]
    more = [
        tr(
            "This algorithm will count the number of points inside each "
            "polygons and run a formula to get the density."
        ),
        tr("number of cases / area * ratio"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_blur():
    title = tr("Blurring")
    intro = tr(
        "Plugin to blur point data, such as health personal data, and "
        "get some statistics about this blurring."
    )
    inputs = [
        tr("Point layer"),
        tr("Radius"),
        tr(
            "Enveloppe : The layer will force the algorithm to have an "
            "intersection between the centroid and this layer. This is like a "
            "mask."
        ),
    ]
    outputs = [tr("Blurred layer (polygon)")]
    more = [
        tr("1 : Creating a buffer (radius r)"),
        picture("blurring_1.png"),
        tr("2 : Random selection of a point in each buffer"),
        picture("blurring_2.png"),
        tr(
            "3 : Creating a buffer around the new point with the same radius. "
            "The initial point is at a maximal distance 2r of the centroid of "
            "the buffer."
        ),
        picture("blurring_3.png"),
        tr("4 : Deleting the random point and the first buffer"),
        picture("blurring_4.png"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_stats_blurring():
    title = tr("Stats")
    intro = tr(
        "With two layers, the plugin will count the number of "
        "intersections between them and produces some stats."
    )
    inputs = [
        tr("Blurred layer"),
        tr("Stats layer : buildings for instanceon layer : administrative boundary"),
    ]
    outputs = [tr("New polygon layer with the density")]
    more = [
        tr("This is usefull if you want to rate your blurring."),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_composite_index():
    title = tr("Composite Index")
    intro = tr("You can create an Unmet Health Index Map using several indicators.")
    inputs = [
        tr("Polygon layer : administrative boundary with the indicators fields"),
        tr("Indicators field"),
        tr("New column"),
    ]
    outputs = [tr("New polygon layer with the Unmet Health Index ")]
    more = [
        tr(
            "This algorithm will  use the Z-scores for each selected indicator to have a Composite index"
        ),
        tr("Please be sure to check the vector direction for each Indicator"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_incidence():
    title = tr("Incidence")
    intro = tr("You can create an incidence map about a disease.")
    inputs = [
        tr("Polygon layer : administrative boundary with a population and case fields"),
        tr("Case field"),
        tr("Population field"),
        tr("Ratio"),
        tr("New column"),
    ]
    outputs = [tr("New polygon layer with the incidence")]
    more = [
        tr(
            "This algorithm will count the number of points inside each "
            "polygons and run a formula to get the incidence."
        ),
        tr("number of cases / population * ratio"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_incidence_point():
    title = tr("Incidence with case layer")
    intro = tr("You can create an incidence map about a disease.")
    inputs = [
        tr("Point layer : disease"),
        tr("Polygon layer : administrative boundary with a population field"),
        tr("Population field"),
        tr("Ratio"),
        tr("New column"),
    ]
    outputs = [tr("New polygon layer with the incidence")]
    more = [
        tr(
            "This algorithm will count the number of points inside each "
            "polygons and run a formula to get the incidence."
        ),
        tr("number of cases / population * ratio"),
    ]
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_autocorrelation(statistic=None):
    title = tr("Autocorrelation")
    stat = statistic or "moran"

    if stat == "geary":
        intro = tr("Local Geary")
        inputs = [
            tr("Polygon layer : administrative boundary with the indicators fields"),
            tr("Field: for local dissimilarity"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("GEARY_G = local Geary statistic"),
            tr("GEARY_P = pseudo p-values"),
            tr("GEARY_S = significance flag"),
        ]
        more = [tr("Local Geary highlights local dissimilarity with neighbors.")]
    elif stat == "g_local":
        intro = tr("Getis-Ord G (Local)")
        inputs = [
            tr("Polygon layer : administrative boundary with the indicators fields"),
            tr("Field: for hotspot/coldspot detection"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("G_LOC = local G statistic"),
            tr("G_Z = standardized z-score"),
            tr("G_P = pseudo p-values"),
            tr("G_HOT = hotspot/coldspot flag"),
        ]
        more = [tr("Getis-Ord G identifies hot and cold spots.")]
    elif stat == "moran_rate":
        intro = tr("Moran Rate")
        inputs = [
            tr("Polygon layer : administrative boundary with cases and population"),
            tr("Field: cases"),
            tr("Population field"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("RATE_P = pseudo p-values"),
            tr("RATE_Z = standardized Moran's I"),
            tr("RATE_Q = quadrant classification"),
            tr("RATE_I = local Moran's I"),
            tr("RATE_C = significance level"),
        ]
        more = [tr("Rate-based Moran's I adjusts for population size.")]
    elif stat == "moran_global":
        intro = tr("Moran (Global)")
        inputs = [
            tr("Polygon layer : administrative boundary with the indicators fields"),
            tr("Field: for global autocorrelation"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("MORAN_I = global Moran's I"),
            tr("MORAN_Z = standardized z-score"),
            tr("MORAN_P = pseudo p-values"),
        ]
        more = [tr("Global Moran's I summarizes overall spatial autocorrelation.")]
    elif stat == "moran_bv_global":
        intro = tr("Moran Bivariate (Global)")
        inputs = [
            tr("Polygon layer : administrative boundary with indicators fields"),
            tr("Field: primary indicator"),
            tr("Second field: secondary indicator"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("MBV_I = global bivariate Moran's I"),
            tr("MBV_Z = standardized z-score"),
            tr("MBV_P = pseudo p-values"),
        ]
        more = [
            tr("Bivariate Moran's I measures spatial association between two fields.")
        ]
    elif stat == "moran_bv_local":
        intro = tr("Moran Bivariate (Local)")
        inputs = [
            tr("Polygon layer : administrative boundary with indicators fields"),
            tr("Field: primary indicator"),
            tr("Second field: secondary indicator"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("MBV_P = pseudo p-values"),
            tr("MBV_Z = standardized Moran's I"),
            tr("MBV_Q = quadrant classification"),
            tr("MBV_I = local bivariate Moran's I"),
            tr("MBV_C = significance level"),
        ]
        more = [tr("Local bivariate Moran highlights co-location patterns.")]
    elif stat == "join_counts_global":
        intro = tr("Join Counts (Global)")
        inputs = [
            tr("Polygon layer : administrative boundary with a binary field"),
            tr("Field: binary indicator (0/1 or thresholded)"),
            tr("Binary threshold: values >= threshold are treated as 1"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("JC_BB = black-black joins"),
            tr("JC_WW = white-white joins"),
            tr("JC_BW = black-white joins"),
            tr("JC_PBB = p-value for BB joins"),
            tr("JC_PBW = p-value for BW joins"),
        ]
        more = [tr("Join counts summarize clustering of a binary outcome.")]
    elif stat == "join_counts_local":
        intro = tr("Join Counts (Local)")
        inputs = [
            tr("Polygon layer : administrative boundary with a binary field"),
            tr("Field: binary indicator (0/1 or thresholded)"),
            tr("Binary threshold: values >= threshold are treated as 1"),
            tr("Contiguity: Rook or Queen weights"),
            tr("Output: shapefile or GeoPackage for results"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("LJC = local join count"),
            tr("LJC_P = pseudo p-values"),
            tr("LJC_S = significance flag"),
        ]
        more = [tr("Local join counts highlight binary clustering hotspots.")]
    else:
        intro = tr("Local Moran / LISA")
        inputs = [
            tr("Polygon layer : administrative boundary with the indicators fields"),
            tr("Field: for calculating the LISA (Local Moran)"),
            tr(
                'Contiguity: Contiguity Based Weights criteria "Rook" (takes as neighbors any pair of cells that share an edge) or "Queen" (include the vertices of the lattice to define contiguitie)'
            ),
            tr("Output: the shapefile were the calcultaions will be available"),
        ]
        outputs = [
            tr("New polygon layer with:"),
            tr("LISA_P = pseudo p-values for each LISA"),
            tr("LISA_Z = standardized Moran's I for each LISA based on permutations"),
            tr(
                "LISA_Q = values or each LISA indicate quandrant location 1 HH, 2 LH, 3 LL, 4 HL"
            ),
            tr("LISA_I = local Moran\’s I values for each LISA"),
            tr("LISA_C = significance level "),
        ]
        more = [
            tr(
                "Local Moran's I measures local autocorrelation quantitatively which results in n values of local spatial autocorrelation, one for each spatial unit."
            ),
        ]

    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_attribute_table():
    title = tr("Export attribute table")
    intro = tr("Export as CSV format without geometry.")
    inputs = [tr("Vector layer")]
    outputs = [tr("A new CSV file")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html


def help_export_kml():
    title = tr("Export KML")
    intro = tr("Export a vector layer as KML")
    inputs = [tr("Choose a vector layer")]
    outputs = [tr("Choose a path and name to store the KML file")]
    more = []
    html = html_table(title, intro, inputs, outputs, more)
    return html
