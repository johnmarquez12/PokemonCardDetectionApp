//
//  CaptureModel.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-11-22.
//

import Foundation
import SwiftUI

@Observable
final class CameraModel : Camera {
    
    var previewSource: PreviewSource { captureService.previewSource }
        /// The current status of the camera, such as unauthorized, running, or failed.
    private(set) var status = CameraStatus.unknown
    
    /// The current state of photo or movie capture.
    private(set) var captureActivity = CaptureActivity.idle
    
    /// The photo features that a person can enable in the user interface.
    private(set) var photoFeatures = PhotoFeatures()
    
    /// A Boolean value that indicates whether the app is currently switching video devices.
    private(set) var isSwitchingVideoDevices = false
    
    /// A Boolean value that indicates whether the app is currently switching capture modes.
    private(set) var isSwitchingModes = false
    
    /// A Boolean value that indicates whether to show visual feedback when capture begins.
    private(set) var shouldFlashScreen = false
    
    /// A thumbnail for the last captured photo or video.
    private(set) var thumbnail: CGImage?
    
    /// An error that indicates the details of an error during photo or movie capture.
    private(set) var error: Error?
    
    private let mediaLibrary = MediaLibrary()
    
    private let captureService = CaptureService()
    
    init() {
        logger.log("Initialized Capture Model")
    }
    
    // MARK: - Changing modes and devices
    
    /// A value that indicates the mode of capture for the camera.
    var captureMode = CaptureMode.photo {
        didSet {
            Task {
                isSwitchingModes = true
                defer { isSwitchingModes = false }
                // Update the configuration of the capture service for the new mode.
                try? await captureService.setCaptureMode(captureMode)
            }
        }
    }
    
    // MARK: - Starting the camera
    /// Start the camera and begin the stream of data.
    func start() async {
        // Verify that the person authorizes the app to use device cameras and microphones.
        guard await captureService.isAuthorized else {
            status = .unauthorized
            return
        }
        do {
            // Start the capture service to start the flow of data.
            try await captureService.start()
            observeState()
            status = .running
        } catch {
            logger.error("Failed to start capture service. \(error)")
            status = .failed
        }
    }
    
    func focusAndExpose(at point: CGPoint) async {
        await captureService.focusAndExpose(at: point)
    }
    
    func zoom(scaleFactor: CGFloat) async {
        await captureService.zoom(scaleFactor: scaleFactor)
    }
    
    func switchVideoDevices() async {
        isSwitchingVideoDevices = true
        defer { isSwitchingVideoDevices = false }
        await captureService.selectNextVideoDevice()
    }
    
    func capturePhoto() async {
        do {
            let photo = try await captureService.capturePhoto(with: photoFeatures.current)
            try await mediaLibrary.save(photo: photo)
        } catch {
            self.error = error
        }
    }
    
    func flashScreen() {
        shouldFlashScreen = true
        withAnimation(.linear(duration: 0.01)) {
            shouldFlashScreen = false
        }
    }
    
    func observeState() {
        Task {
            // Await new thumbnails that the media library generates when saving a file.
            for await thumbnail in mediaLibrary.thumbnails.compactMap({ $0 }) {
                self.thumbnail = thumbnail
            }
        }
        
        Task {
            // Await new capture activity values from the capture service.
            for await activity in await captureService.$captureActivity.values {
                if activity.willCapture {
                    // Flash the screen to indicate capture is starting.
                    flashScreen()
                } else {
                    // Forward the activity to the UI.
                    captureActivity = activity
                }
            }
        }
        
//        Not supporting HDR
        
//        Task {
//            // Await updates to the capabilities that the capture service advertises.
//            for await capabilities in await captureService.$captureCapabilities.values {
//                isHDRVideoSupported = capabilities.isHDRSupported
//            }
//        }
    }

}
