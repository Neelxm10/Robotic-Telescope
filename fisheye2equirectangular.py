# From Paul Bourke's article https://paulbourke.net/dome/dualfish2sphere/
# Another example implementation here: https://github.com/ArashJavan/fisheye2equirect

# FIRST HAVE TO CALIBRATE. SEE: https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0
# and https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-part-2-13990f1b157f to adjust for distortion
# put center and radius in fisheye_equirectangular function

import cv2
import numpy as np
import argparse

# APERTURE = 210 * np.pi / 180

def linear_interpolation(y0, y1, x0, x1, x):
    m = (y1 - y0) / (x1 - x0)
    b = y0
    return m * (x - x0) + b

# "Fisheye image" -> radially symmetric in longitude, and with latitude proportional to the radius from the center of the fisheye circle

def fisheye_to_equirectangular(src_img, aperture, h_dst, w_dst):
    h_src, w_src = src_img.shape[:2]
    dst_img = np.zeros((h_dst, w_dst, 3), dtype=np.uint8)

    max_longitude = aperture / 2
    max_latitude = aperture / 4

    for y in range(h_dst):
        y_dst_norm = linear_interpolation(-1, 1, 0, h_dst, y)

        for x in range(w_dst):
            x_dst_norm = linear_interpolation(-1, 1, 0, w_dst, x)

            # Calc spherical coordinates
            # longitude = x_dst_norm * np.pi # Assumes a full 360 view (when using two pinhole images)
            # latitude = y_dst_norm * np.pi / 2
            longitude = x_dst_norm * max_longitude
            latitude = y_dst_norm * max_latitude

            # Spherical coords to Cartesian
            p_x = np.cos(latitude) * np.cos(longitude)
            p_y = np.cos(latitude) * np.sin(longitude)
            p_z = np.sin(latitude)

            # Map Cartesian to fisheye
            p_xz = np.sqrt(p_x**2 + p_z**2)
            r = 2 * np.arctan2(p_xz, p_y) / aperture
            theta = np.arctan2(p_z, p_x)

            input_x_norm = r * np.cos(theta)
            input_y_norm = r * np.sin(theta)

            input_x = linear_interpolation(0, w_src, -1, 1, input_x_norm)
            input_y = linear_interpolation(0, h_src, -1, 1, input_y_norm)

            if 0 <= input_x < w_src and 0 <= input_y < h_src:
                dst_img[y, x, :] = src_img[int(input_y), int(input_x), :]

    return dst_img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a fisheye image to an equirectangular projection")
    parser.add_argument("--input", required=True, help="Path to the input fisheye image")
    parser.add_argument("--output", required=True, help="Path to save the output equirectangular image")
    parser.add_argument("--width", type=int, default=2000, help="Width of the output image")
    parser.add_argument("--height", type=int, default=1000, help="Height of the output image")
    #parser.add_argument("--center", nargs=2, type=int, required=True, help="Center of the fisheye image (x, y)")
    #parser.add_argument("--radius", type=int, required=True, help="Radius of the fisheye circle in pixels")
    parser.add_argument("--aperture", type=float, default=210, help="Camera aperture in degrees")

    args = parser.parse_args()

    # Load the input image
    src_img = cv2.imread(args.input)
    if src_img is None:
        raise ValueError("Failed to load input image")

    # Convert aperture from degrees to radians
    aperture_rad = args.aperture * np.pi / 180

    # Perform fisheye to equirectangular transformation
    equi_img = fisheye_to_equirectangular(
        src_img, 
        #center=tuple(args.center), radius=args.radius,
        aperture=aperture_rad, h_dst=args.height, w_dst=args.width
    )

    # Save the output image
    cv2.imwrite(args.output, equi_img)
    print(f"Output saved to {args.output}")
