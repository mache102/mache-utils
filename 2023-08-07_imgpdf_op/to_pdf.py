import argparse
import os

from PIL import Image
from tkinter import Tk, filedialog
import pytesseract

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')

def convert_images_to_pdf(args):

    input_fp = args.input
    output_fn = args.output
    dpi = args.dpi
    language = args.language.lower()
    
    images = []
    for fn in sorted(os.listdir(input_fp)):
        if fn.lower().endswith(IMAGE_EXTENSIONS):
            images.append(os.path.join(input_fp, fn))

    if not images:
        print("No images found in the input folder.")
        return

    pdf_images = []
    for img_path in images:
        with Image.open(img_path) as img:
            text = pytesseract.image_to_string(img, lang=language)
            if text.strip():  # Check if OCR detected any text
                img_with_text = Image.new("RGB", img.size, "white")
                img_with_text.paste(img, mask=img.split()[3])
                pdf_images.append(img_with_text)
            else:
                pdf_images.append(img)

    pdf_images[0].save(output_fn, save_all=True, append_images=pdf_images[1:], dpi=(dpi, dpi))

    print(f"PDF successfully created: {output_fn}")


def parse_opt():
    parser = argparse.ArgumentParser(description='Converts a folder of images to a PDF')

    parser.add_argument('--input', type=str, default='', help='input folder')
    parser.add_argument('--output', type=str, default='', help='output fn')
    parser.add_argument('--color', type=str, default='color', 
                        choices=['color', 'grayscale', 'bandw'], 
                        help='color option (full color, grayscale, black and white)')
    parser.add_argument('--dpi', type=int, default=300, help='dpi of output PDF')
    parser.add_argument('--language', type=str, default='eng', 
                        choices=['eng', 'chi', 'deu', 'fra', 'spa'], 
                        help='language for OCR (English, Chinese, German, French, Spanish)')

    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_opt()

    if not args.input:
        # If --input not provided, use tkinter to select the input folder interactively
        root = Tk()
        root.withdraw()
        args.input = filedialog.askdirectory(title='Select Input Folder')

    if not args.output:
        # If --output not provided, use tkinter to select the output fn interactively
        root = Tk()
        root.withdraw()
        args.output = filedialog.asksaveasfilename(defaultextension=".pdf", title='Select Output PDF File')

    convert_images_to_pdf(args)

if __name__ == "__main__":
    main()
