//
//  CardDetectionManager.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-12-05.
//

import UIKit
import Vision

class CardDetectionManager {
    
    private var cardDetectionModel: CardDetection
    private var classes: [String]
    
    lazy var detectionRequest:VNCoreMLRequest! = {
        do {
            let vnModel = try VNCoreMLModel(for: cardDetectionModel.model)
            let request = VNCoreMLRequest(model: vnModel)
            return request
        } catch let error {
            fatalError("mlmodel error.")
        }
    }()
    
    init(cardDetectionModel: CardDetection) {
        //
        self.cardDetectionModel = cardDetectionModel
        self.classes = cardDetectionModel.model.modelDescription.classLabels as! [String]
    }
    
    func detectCards(in photo: Photo) {
       
        
        guard let image = photoToUIImage(photo: photo) else {
            logger.error("Failed to convert photo to UIImage")
            return
        }
        
        guard let pixelBuffer = imageToPixelBuffer(image: image) else {
            logger.error("Failed to convert image to pixel buffer")
            return
        }
        
        do {
            let prediction: CardDetectionOutput = try cardDetectionModel.prediction(image: pixelBuffer)
            
        } catch {
            logger.error("Error during prediction: \(error)")
        }
    }
    
    private func imageToPixelBuffer(image: UIImage) -> CVPixelBuffer? {
        // Get the image size and ensure it's not empty
        let size = image.size
        let width = Int(size.width)
        let height = Int(size.height)
        
        // Create a pixel buffer attribute dictionary
        let options: [CFString: Any] = [
            kCVPixelBufferCGImageCompatibilityKey: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey: true
        ]
        
        // Create an empty pixel buffer
        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(kCFAllocatorDefault,
                                         width,
                                         height,
                                         kCVPixelFormatType_32BGRA,
                                         options as CFDictionary,
                                         &pixelBuffer)
        
        guard status == kCVReturnSuccess, let buffer = pixelBuffer else {
            print("Error: Unable to create pixel buffer.")
            return nil
        }
        
        // Lock the pixel buffer to get access to its memory
        CVPixelBufferLockBaseAddress(buffer, .readOnly)
        
        // Get a context to draw into the pixel buffer
        let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer),
                                width: width,
                                height: height,
                                bitsPerComponent: 8,
                                bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
                                space: CGColorSpaceCreateDeviceRGB(),
                                bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipFirst.rawValue).rawValue)
        
        // Draw the image into the pixel buffer context
        guard let cgImage = image.cgImage else {
            print("Error: Unable to get CGImage from UIImage.")
            return nil
        }
        context?.draw(cgImage, in: CGRect(x: 0, y: 0, width: size.width, height: size.height))
        
        // Unlock the pixel buffer
        CVPixelBufferUnlockBaseAddress(buffer, .readOnly)
        
        return buffer
    }
    
    private func photoToUIImage(photo: Photo) -> UIImage? {
        guard let image = UIImage(data: photo.data) else {
            logger.error("Failed to convert photo data to UIImage")
            return nil
        }
        
        return image
    }
}
