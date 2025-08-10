from PIL import Image, ImageChops
import random

def apply_chromatic_jitter_single_frame(image, max_offset=5):
    """
    Applies a chromatic jitter (RGB split) effect to a single image.

    Args:
        image (PIL.Image.Image): The input image (should be in 'RGB' or 'RGBA' mode).
        max_offset (int): The maximum pixel offset for each color channel.

    Returns:
        PIL.Image.Image: The image with chromatic jitter applied.
    """
    if max_offset == 0: # Optimization: No jitter if offset is 0
        return image.copy()

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")

    alpha = None
    if image.mode == "RGBA":
        r, g, b, alpha = image.split()
        original_rgb_image = Image.merge("RGB", (r, g, b))
    else:
        original_rgb_image = image

    r, g, b = original_rgb_image.split()

    offset_r_x = random.randint(-max_offset, max_offset)
    offset_r_y = random.randint(-max_offset, max_offset)
    offset_g_x = random.randint(-max_offset, max_offset)
    offset_g_y = random.randint(-max_offset, max_offset)
    offset_b_x = random.randint(-max_offset, max_offset)
    offset_b_y = random.randint(-max_offset, max_offset)

    shifted_r = ImageChops.offset(r, offset_r_x, offset_r_y)
    shifted_g = ImageChops.offset(g, offset_g_x, offset_g_y)
    shifted_b = ImageChops.offset(b, offset_b_x, offset_b_y)

    if alpha:
        return Image.merge("RGBA", (shifted_r, shifted_g, shifted_b, alpha))
    else:
        return Image.merge("RGB", (shifted_r, shifted_g, shifted_b))


def apply_block_shift_single_frame(image, max_shift=10, block_size=5, horizontal=True):
    """
    Applies a block-shift jitter effect to a single image.

    Args:
        image (PIL.Image.Image): The input image.
        max_shift (int): The maximum pixel offset for each block.
        block_size (int): The height/width of each block for shifting.
        horizontal (bool): If True, shifts horizontal blocks; if False, shifts vertical blocks.

    Returns:
        PIL.Image.Image: The image with block shift applied.
    """
    if max_shift == 0: # Optimization: No shift if offset is 0
        return image.copy()

    width, height = image.size
    new_image = Image.new(image.mode, (width, height), (0, 0, 0, 0) if 'A' in image.mode else (0, 0, 0))

    if horizontal:
        for y_start in range(0, height, block_size):
            y_end = min(y_start + block_size, height)
            shift_x = random.randint(-max_shift, max_shift)
            block = image.crop((0, y_start, width, y_end))
            paste_x = (0 + shift_x) % width
            new_image.paste(block, (paste_x, y_start))
            if paste_x + block.width > width:
                remaining_width = (paste_x + block.width) - width
                wrapped_block = block.crop((block.width - remaining_width, 0, block.width, block.height))
                new_image.paste(wrapped_block, (0, y_start))
    else: # Vertical shift
        for x_start in range(0, width, block_size):
            x_end = min(x_start + block_size, width)
            shift_y = random.randint(-max_shift, max_shift)
            block = image.crop((x_start, 0, x_end, height))
            paste_y = (0 + shift_y) % height
            new_image.paste(block, (x_start, paste_y))
            if paste_y + block.height > height:
                remaining_height = (paste_y + block.height) - height
                wrapped_block = block.crop((0, block.height - remaining_height, block.width, block.height))
                new_image.paste(wrapped_block, (x_start, 0))

    return new_image

def generate_jittered_frames(image, frames=20,
                             enable_chromatic_jitter=True, chrom_max_offset=3,
                             enable_block_shift=True, block_max_shift=10,
                             block_size=5, horizontal_block_shift=True):
    """
    Generates a list of frames with conditional chromatic and/or block-shift jitter effects.

    Args:
        image (PIL.Image.Image): The input image.
        frames (int): The number of frames in the animated GIF.
        enable_chromatic_jitter (bool): Whether to apply chromatic jitter.
        chrom_max_offset (int): Max pixel offset for chromatic jitter.
        enable_block_shift (bool): Whether to apply block shift.
        block_max_shift (int): Max pixel offset for block shift.
        block_size (int): The height/width of each block for shifting.
        horizontal_block_shift (bool): If True, shifts horizontal blocks; if False, shifts vertical blocks.

    Returns:
        list: A list of PIL.Image.Image objects, each representing a jittered frame.
    """
    all_frames = []

    for _ in range(frames):
        current_frame_image = image.copy() # Start each frame with a clean copy of the original

        if enable_chromatic_jitter:
            current_frame_image = apply_chromatic_jitter_single_frame(current_frame_image, chrom_max_offset)

        if enable_block_shift:
            current_frame_image = apply_block_shift_single_frame(current_frame_image, block_max_shift, block_size, horizontal_block_shift)

        all_frames.append(current_frame_image)
    return all_frames


def create_animated_jitter_gif(input_png_path, output_gif_path, frames=20,
                               enable_chromatic_jitter=True, chrom_max_offset=3,
                               enable_block_shift=True, block_max_shift=10,
                               block_size=5, horizontal_block_shift=True, duration=75):
    """
    Creates an animated GIF with conditional chromatic and/or block-shift jitter effects.

    Args:
        input_png_path (str): The path to the input PNG image.
        output_gif_path (str): The path to save the output animated GIF.
        frames (int): The number of frames in the animated GIF.
        enable_chromatic_jitter (bool): Whether to apply chromatic jitter.
        chrom_max_offset (int): Max pixel offset for chromatic jitter.
        enable_block_shift (bool): Whether to apply block shift.
        block_max_shift (int): Max pixel offset for block shift.
        block_size (int): The height/width of each block for shifting.
        horizontal_block_shift (bool): If True, shifts horizontal blocks; if False, shifts vertical blocks.
        duration (int): The duration (in milliseconds) of each frame in the GIF.
    """
    try:
        img = Image.open(input_png_path).convert("RGBA") # Always work with RGBA for consistency
    except FileNotFoundError:
        print(f"Error: Input PNG file not found at '{input_png_path}'")
        return
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    effect_description = []
    if enable_chromatic_jitter:
        effect_description.append(f"chromatic jitter (offset: {chrom_max_offset})")
    if enable_block_shift:
        block_type = "horizontal" if horizontal_block_shift else "vertical"
        effect_description.append(f"{block_type} block shift (max_shift: {block_max_shift}, block_size: {block_size})")

    if not effect_description:
        print("Warning: No jitter effects enabled. Creating a static GIF of the original image.")
        effect_description.append("no effects")

    print(f"Generating GIF for '{input_png_path}' with {', '.join(effect_description)} and {frames} frames...")

    jittered_frames = generate_jittered_frames(
        img, frames,
        enable_chromatic_jitter, chrom_max_offset,
        enable_block_shift, block_max_shift,
        block_size, horizontal_block_shift
    )

    if not jittered_frames:
        print("No frames were generated. Aborting GIF creation.")
        return

    print(f"Saving animated GIF to '{output_gif_path}'...")
    try:
        jittered_frames[0].save(
            output_gif_path,
            save_all=True,
            append_images=jittered_frames[1:],
            optimize=False,
            duration=duration,
            loop=0,
            disposal=2
        )
        print("GIF created successfully!")
    except Exception as e:
        print(f"Error saving GIF: {e}")

if __name__ == "__main__":
    input_file = r"activity-graph.png" # Make sure you have this PNG file

    # --- EXAMPLE 1: Chromatic Jitter ONLY ---
    print("\n--- Example 1: Chromatic Jitter ONLY ---")
    create_animated_jitter_gif(
        input_png_path=input_file,
        output_gif_path="output_chromatic_only.gif",
        frames=40,
        enable_chromatic_jitter=True,    # Turn ON chromatic
        chrom_max_offset=3,
        enable_block_shift=True,        # Turn OFF block shift
        block_max_shift=3,               # Not used when disabled, but good to keep consistent
        block_size=3,                    # Not used when disabled
        horizontal_block_shift=True,     # Not used when disabled
        duration=75
    )

    print("\n--- Instructions ---")
    print(f"1. Make sure you have a PNG file named '{input_file}' in the same directory as this script.")
    print(f"2. Run this script: python your_script_name.py")
    print(f"3. Multiple animated GIFs will be created based on the examples in the __main__ block.")
    print("\n--- To install Pillow ---")
    print("If you don't have Pillow installed, open your terminal or command prompt and run:")
    print("pip install Pillow")