#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2015-2022 Blender Authors
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import sys


# When run from inside Blender, render and exit.
try:
    import bpy
    inside_blender = True
except ImportError:
    inside_blender = False

SET_COMPOSITOR_DEVICE_SCRIPT = "import bpy; " \
    "bpy.data.scenes[0].render.compositor_device = 'CPU'"


def get_arguments(filepath, output_filepath):
    return [
        "--background",
        "--factory-startup",
        "--enable-autoexec",
        "--debug-memory",
        "--debug-exit-on-error",
        filepath,
        "-P", os.path.realpath(__file__),
        "--python-expr", SET_COMPOSITOR_DEVICE_SCRIPT,
        "-o", output_filepath,
        "-F", "PNG",
        "-f", "1"]


def create_argparse():
    parser = argparse.ArgumentParser(
        description="Run test script for each blend file in TESTDIR, comparing the render result with known output."
    )
    parser.add_argument("--blender", required=True)
    parser.add_argument("--testdir", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--oiiotool", required=True)
    parser.add_argument('--batch', default=False, action='store_true')
    return parser


def main():
    parser = create_argparse()
    args = parser.parse_args()

    from modules import render_report
    report = render_report.Report("Compositor CPU", args.outdir, args.oiiotool)
    report.set_pixelated(True)
    report.set_reference_dir("compositor_cpu_renders")

    if os.path.basename(args.testdir) == 'filter':
        # Temporary change to pass OpenImageDenoise test with both 1.3 and 1.4.
        report.set_fail_threshold(0.05)
    elif os.path.basename(args.testdir) == 'matte':
        # The node_keying_matte.blend test is very sensitive to the exact values in the
        # input image. It makes it hard to precisely match results on different systems
        # (with and without SSE, i.e.), especially when OCIO has different precision for
        # the exponent transform on different platforms.
        report.set_fail_threshold(0.06)
        report.set_fail_percent(2)

    ok = report.run(args.testdir, args.blender, get_arguments, batch=args.batch)

    sys.exit(not ok)


if not inside_blender and __name__ == "__main__":
    main()
