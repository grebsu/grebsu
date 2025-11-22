import re
import argparse
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import List

# Define the pattern to find the specific GitHub stats URLs
URL_PATTERN = r'src="(https://github-stats-rho-seven.vercel.app/api/pin/.*?)"'

# Define the colors for the rainbow pattern (hex codes without '#')
RAINBOW_COLORS = [
    '007fff',  # Azure
    '0000ff',  # Blue
    '4b0082',  # Indigo
    '9400d3',  # Violet
    'ff00ff',  # Magenta
    'ff0000',  # Red
    'ff4500',  # Red-Orange
    'ff7f00',  # Orange
    'ffbf00',  # Amber
    'ffff00',  # Yellow
    '7fff00',  # Lime Green
    '00ff00',  # Green
    '00ff7f',  # Spring Green
    '00ffff',  # Cyan
]

def modify_url_color(url: str, new_color: str) -> str:
    """
    Safely modifies the 'icon_color' query parameter of a URL.
    Adds the parameter if it doesn't exist, otherwise updates it.
    """
    # Parse the URL into its components
    parsed_url = urlparse(url)
    
    # Parse the query string into a dictionary
    # `keep_blank_values=True` preserves parameters without values
    query_params = parse_qs(parsed_url.query, keep_blank_values=True)
    
    # Update or add the icon_color parameter
    query_params['icon_color'] = [new_color]
    
    # Encode the modified query parameters back into a string
    new_query_string = urlencode(query_params, doseq=True)
    
    # Rebuild the URL with the new query string
    new_url_parts = list(parsed_url)
    new_url_parts[4] = new_query_string # Index 4 is the query part
    
    return urlunparse(new_url_parts)

def process_readme(content: str, mode: str, color: str = None, colors: List[str] = None) -> str:
    """
    Finds all matching URLs in the README content and updates them
    based on the selected mode ('single' or 'rainbow').
    """
    found_urls = re.findall(URL_PATTERN, content)
    
    if not found_urls:
        print("No matching GitHub stats URLs found.")
        return content

    modified_content = content
    
    if mode == 'single':
        if not color:
            raise ValueError("A color must be provided for single color mode.")
        print(f"Setting all {len(found_urls)} icons to color: {color}")
        for url in found_urls:
            new_url = modify_url_color(url, color)
            modified_content = modified_content.replace(url, new_url)
            
    elif mode == 'rainbow':
        if not colors:
            raise ValueError("A list of colors must be provided for rainbow mode.")
        print(f"Applying rainbow pattern to {len(found_urls)} icons...")
        for i, url in enumerate(found_urls):
            # Cycle through the rainbow colors
            color_to_use = colors[i % len(colors)]
            new_url = modify_url_color(url, color_to_use)
            modified_content = modified_content.replace(url, new_url)
            
    return modified_content

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Modify icon colors in GitHub stats links in a README file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("input_file", help="Path to the input README.md file.")
    parser.add_argument("output_file", help="Path to save the modified README.md file.")
    
    # Create a mutually exclusive group for color options
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--color",
        metavar="HEX",
        help="A single hex color (without '#') to apply to all icons."
    )
    mode_group.add_argument(
        "--rainbow",
        action="store_true",
        help="Apply a rainbow color pattern to the icons."
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input_file}'")
        return

    if args.rainbow:
        new_content = process_readme(readme_content, mode='rainbow', colors=RAINBOW_COLORS)
    else: # args.color is guaranteed to be set if not rainbow
        # Simple validation for hex color format
        if not re.match(r'^[a-fA-F0-9]{3,6}$', args.color):
             print(f"Warning: '{args.color}' doesn't look like a valid hex code. Proceeding anyway.")
        new_content = process_readme(readme_content, mode='single', color=args.color)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"\n✅ Success! Modified content saved to '{args.output_file}'")


if __name__ == "__main__":
    main()
