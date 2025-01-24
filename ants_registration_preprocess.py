#!/usr/bin/env python

import itk
import argparse
import textwrap

def preprocess_image(input_image_path, winsorize_quantiles=(0.0, 1.0), dimension=3):
    if dimension not in [2, 3]:
        raise ValueError("Invalid dimension. Acceptable choices are 2 or 3.")

    # Read the input image
    input_image = itk.imread(input_image_path, itk.F)

    # Compute histogram for winsorization
    histogram_filter = itk.ImageToHistogramFilter[type(input_image)].New()
    histogram_filter.SetInput(input_image)
    histogram_filter.SetAutoMinimumMaximum(True)
    histogram_filter.SetHistogramSize([256] * dimension)
    histogram_filter.SetMarginalScale(10.0)
    histogram_filter.Update()

    # Calculate quantile thresholds
    histogram = histogram_filter.GetOutput()
    lower_value = histogram.Quantile(0, winsorize_quantiles[0])
    upper_value = histogram.Quantile(0, winsorize_quantiles[1])

    # Apply intensity windowing
    windowing_filter = itk.IntensityWindowingImageFilter.New(Input=input_image)
    windowing_filter.SetWindowMinimum(lower_value)
    windowing_filter.SetWindowMaximum(upper_value)
    windowing_filter.SetOutputMinimum(0.0)
    windowing_filter.SetOutputMaximum(1.0)
    windowing_filter.Update()

    processed_image = windowing_filter.GetOutput()

    return processed_image


# Helps with CLI help formatting
class RawDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=RawDefaultsHelpFormatter, add_help = False,
                                     description = textwrap.dedent(
    '''
    Preprocess an image with winsorization and optional histogram matching.

    This script is designed to provide the same pre-processing as antsRegistration does internally. Images are winsorized
    and the moving image is optionally histogram-matched to the fixed image.

    The script is designed to for evaluation purposes, you can have antsRegistration do the same things with the '-w'
    option for winsorization and the '-u' option for histogram matching.
    '''))
    parser.add_argument("-d", "--dimension", type=int, default=3,
                        help="Dimension of the input image (default 3). Acceptable choices are 2 or 3.")
    parser.add_argument("-w", "--winsorize-quantiles", nargs=2, type=float, default=[0.0, 1.0],
                        metavar=("LOWER", "UPPER"),
                        help="Lower and upper quantiles for winsorization (default 0 1).")
    parser.add_argument("-u", "--histogram-match", help="Histogram match the moving image to the fixed image.",
                        action="store_true")
    parser.add_argument("-h", "--help", action="help", help="show this help message and exit")

    # positional
    parser.add_argument("fixed_image", help="Path to the fixed image.")
    parser.add_argument("moving_image", help="Path to the moving image.")
    parser.add_argument("output_root", help="Path to save the processed images.")

    args = parser.parse_args()

    print("Winsorizing and normalizing intensities")

    processed_fixed = preprocess_image(
        args.fixed_image,
        tuple(args.winsorize_quantiles),
        args.dimension
    )

    processed_moving = preprocess_image(
        args.moving_image,
        tuple(args.winsorize_quantiles),
        args.dimension
    )

    # If histogram matching source is provided, preprocess it and perform histogram matching
    if args.histogram_match:
        print("Histogram matching moving image to fixed image")
        histogram_matching_filter = itk.HistogramMatchingImageFilter[type(processed_fixed), type(processed_fixed)].New()
        histogram_matching_filter.SetSourceImage(processed_moving)
        histogram_matching_filter.SetReferenceImage(processed_fixed)
        histogram_matching_filter.SetNumberOfHistogramLevels(256)
        histogram_matching_filter.SetNumberOfMatchPoints(12)
        histogram_matching_filter.ThresholdAtMeanIntensityOn()
        histogram_matching_filter.Update()

        processed_moving = histogram_matching_filter.GetOutput()

    # Write the processed image to file
    itk.imwrite(processed_fixed, f"{args.output_root}_preprocessed_fixed.nii.gz")
    itk.imwrite(processed_moving, f"{args.output_root}_preprocessed_moving.nii.gz")
    print(f"Output written to {args.output_root}_preprocessed_[fixed,moving.nii.gz]")