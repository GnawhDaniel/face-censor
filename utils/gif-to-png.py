from PIL import Image

def gif_to_png_all_frames(gif_path, output_dir="output_frames"):
    """
    Extracts all frames of an animated GIF to separate PNG images.

    Args:
        gif_path (str): The path to the input GIF file.
        output_dir (str): The directory to save the output PNG files.
    """
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with Image.open(gif_path) as img:
            for i in range(img.n_frames):
                img.seek(i)
                frame = img.convert("RGBA")
                frame_path = os.path.join(output_dir, f"frame_{i}.png")
                frame.save(frame_path)
                print(f"Saved frame {i+1}/{img.n_frames} to '{frame_path}'")
        print(f"Successfully extracted all frames from '{gif_path}' to '{output_dir}'.")
    except FileNotFoundError:
        print(f"Error: GIF file not found at '{gif_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
gif_file = "bocchi.gif"  # Replace with your animated GIF file path
output_directory = "extracted_pngs"
gif_to_png_all_frames(gif_file, output_directory)