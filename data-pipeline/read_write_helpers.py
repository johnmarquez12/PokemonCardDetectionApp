import cv2
from pathlib import Path

def save_obb_points(obb_points, filename, output_dir: Path, class_index):
    output_file = output_dir / f"{filename}.txt"
    output_dir.mkdir(parents=True, exist_ok=True)

    with output_file.open('w') as file:
        
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = obb_points
        
        # Format the bounding box into the YOLO OBB format
        formatted_line = f"{class_index} {x1:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x3:.6f} {y3:.6f} {x4:.6f} {y4:.6f}\n"
        
        # Write the formatted line to the file
        file.write(formatted_line)

def save_image(image: cv2.typing.MatLike, filename, output_dir: Path, extension='.jpg'):
    output_file = output_dir / f"{filename}{extension}"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_file), image)

    if success:
        print(f"Image saved successfully to {output_file}")
    else:
        print(f"Failed to save image: {output_file}")

def read_obb_points(filepath: Path):
    with filepath.open('r') as file:
        lines = file.readlines()
        # Iterate over each line in the file
        for line in lines:
            # Split the line by spaces to extract the values
            values = line.strip().split()
            
            # Next 8 values are the coordinates (x1, y1, x2, y2, x3, y3, x4, y4)
            x1, y1 = float(values[1]) , float(values[2]) 
            x2, y2 = float(values[3]) , float(values[4]) 
            x3, y3 = float(values[5]) , float(values[6]) 
            x4, y4 = float(values[7]) , float(values[8]) 
            
            # Create an array of points (OpenCV expects the points in integer format)
            return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        

def save_all(filename, image: cv2.typing.MatLike, points, output_path: Path):
    save_obb_points(points, filename, output_path / "labels", 0)
    save_image(image, filename, output_path / "images")