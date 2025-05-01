# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 GeoPublicHealth
                                 A QGIS plugin

                              -------------------
        begin                : 2014-08-20
        copyright            : (C) 2014 by Etienne Trimaille
                                (C) 2020-2024 by ePublicHealth/GeoPublicHealth Team
        email                : etienne@trimaille.eu
                                manuel.vidaurre@gmail.com
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

# Core QGIS Imports for Processing
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingFeatureSource,
    QgsFeatureSink,
    QgsWkbTypes,
    QgsFields,
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    Qgis # Needed for warning levels if using feedback.reportError
)
# PyQt Imports
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, QCoreApplication

# Plugin specific imports
from GeoPublicHealth.src.core.blurring.blur import Blur
from GeoPublicHealth.src.core.blurring.layer_index import LayerIndex
from GeoPublicHealth.src.utilities.resources import resource
from GeoPublicHealth.src.core.exceptions import GeoPublicHealthException

class BlurringGeoAlgorithm(QgsProcessingAlgorithm):
    """
    QGIS Processing algorithm for blurring a point layer.
    Creates polygon buffers around randomly offset points based on input points.
    """

    # Parameter and Output constants
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    RADIUS_FIELD = 'RADIUS_FIELD'
    RADIUS_EXPORT = 'RADIUS_EXPORT'
    CENTROID_EXPORT = 'CENTROID_EXPORT'
    # DISTANCE_EXPORT seems unused in original code, omitting unless needed
    ENVELOPE_LAYER = 'ENVELOPE_LAYER'

    def initAlgorithm(self, config):
        """Defines the input parameters and output specifications for the algorithm."""

        # Input point layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_LAYER,
                self.tr('Point layer to blur'),
                [QgsProcessing.TypeVectorPoint] # Accepts only point layers
            )
        )

        # Blurring radius
        self.addParameter(
            QgsProcessingParameterNumber(
                self.RADIUS_FIELD,
                self.tr('Radius (map units)'),
                type=QgsProcessingParameterNumber.Double, # Specify number type
                defaultValue=500.00,
                minValue=0.0 # Radius cannot be negative
            )
        )

        # Optional envelope layer (polygon)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.ENVELOPE_LAYER,
                self.tr('Envelope layer (optional mask)'),
                [QgsProcessing.TypeVectorPolygon], # Accepts only polygon layers
                optional=True # This parameter is not mandatory
            )
        )

        # Option to add radius to output attributes
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RADIUS_EXPORT,
                self.tr('Add radius to attribute table'),
                defaultValue=False
            )
        )

        # Option to add centroid coordinates to output attributes
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CENTROID_EXPORT,
                self.tr('Add centroid coordinates (X, Y) to attribute table'),
                defaultValue=False
            )
        )

        # Output layer (sink)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER,
                self.tr('Blurred Layer (Output)'),
                QgsProcessing.TypeVectorPolygon # Output is always polygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Main execution logic of the blurring algorithm."""

        # --- Get Parameters ---
        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if source is None:
            raise GeoPublicHealthException(self.tr("Input layer not found."))

        radius = self.parameterAsDouble(parameters, self.RADIUS_FIELD, context)
        export_radius = self.parameterAsBool(parameters, self.RADIUS_EXPORT, context)
        export_centroid = self.parameterAsBool(parameters, self.CENTROID_EXPORT, context)
        envelope_layer = self.parameterAsVectorLayer(parameters, self.ENVELOPE_LAYER, context)

        # --- Prepare Envelope Index (if provided) ---
        vector_layer_envelope_index = None
        if envelope_layer:
            feedback.pushInfo(self.tr("Preparing envelope index..."))
            # Check CRS compatibility
            if source.sourceCrs() != envelope_layer.crs():
                 feedback.reportError(
                     self.tr("Input layer and Envelope layer must have the same CRS."), fatalError=True)
                 return {}
            # Create spatial index for the envelope layer
            vector_layer_envelope_index = LayerIndex(envelope_layer)
            feedback.pushInfo(self.tr("Envelope index created."))


        # --- Prepare Output ---
        out_fields = QgsFields()
        # Copy fields from the source layer
        out_fields.extend(source.fields())

        # Add new fields based on export options
        if export_radius:
            out_fields.append(QgsField("Radius", QVariant.Double)) # Use Double for radius
        if export_centroid:
            out_fields.append(QgsField("X_centroid", QVariant.Double)) # Use Double for coordinates
            out_fields.append(QgsField("Y_centroid", QVariant.Double)) # Use Double for coordinates

        # Get the output sink and destination ID
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            out_fields,
            QgsWkbTypes.Polygon, # Output geometry type is Polygon
            source.sourceCrs() # Output CRS matches input CRS
        )
        if sink is None:
             raise GeoPublicHealthException(self.tr("Could not create output layer."))

        # --- Initialize Blurring Algorithm ---
        feedback.pushInfo(self.tr("Starting blurring process..."))
        algo = Blur(
            radius,
            vector_layer_envelope_index,
            export_radius,
            export_centroid
        )

        # --- Process Features ---
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Check for cancellation
            if feedback.isCanceled():
                break

            try:
                # Perform blurring
                blurred_feature = algo.blur(feature) # algo.blur returns a QgsFeature
                # Add the processed feature to the output sink
                sink.addFeature(blurred_feature, QgsFeatureSink.FastInsert)
            except GeoPublicHealthException as e:
                # Report errors encountered during blurring (e.g., point outside envelope)
                feedback.reportError(f"Error processing feature ID {feature.id()}: {e.msg}", fatalError=False)
                # Optionally skip the feature or handle the error differently
                continue # Skip this feature and continue with the next

            # Update progress feedback
            feedback.setProgress(int(current * total))

        # Check if the process was cancelled after the loop
        if feedback.isCanceled():
             feedback.pushInfo(self.tr("Processing cancelled."))
             # Depending on sink type, might need cleanup or finalization steps here
             return {} # Return empty dictionary on cancellation

        feedback.pushInfo(self.tr("Blurring process completed."))

        # Return the destination ID for the output layer
        return {self.OUTPUT_LAYER: dest_id}

    # --- Metadata Methods ---
    def name(self):
        """Returns the unique algorithm name."""
        return 'geopublichealth_blurring' # Use lowercase and underscores

    def displayName(self):
        """Returns the translated algorithm name."""
        return self.tr('Blur Point Layer')

    def group(self):
        """Returns the group name for organization in Processing."""
        return self.tr('GeoPublicHealth Tools')

    def groupId(self):
        """Returns the unique group ID."""
        return 'geopublichealthtools' # Use lowercase

    def tr(self, string):
        """Translates a string using the plugin's context."""
        return QCoreApplication.translate('BlurringGeoAlgorithm', string)

    def createInstance(self):
        """Creates a new instance of the algorithm."""
        return BlurringGeoAlgorithm()

    def helpUrl(self):
         """Provides a link to more detailed help (optional)."""
         # Replace with an actual URL if help exists
         return "https://github.com/ePublicHealth/GeoPublicHealth/wiki" # Example URL

    def shortHelpString(self):
        """Provides a brief description for the Processing GUI."""
        return self.tr(
            'Blurs point locations by creating polygon buffers around randomly offset points.\n'
            'Optionally uses an envelope layer as a mask and adds radius/centroid attributes.'
        )

    def icon(self):
         """Returns the icon for the algorithm."""
         return QIcon(resource('blur.png'))
