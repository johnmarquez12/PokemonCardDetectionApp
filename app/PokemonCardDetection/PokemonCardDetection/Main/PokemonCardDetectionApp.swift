//
//  PokemonCardDetectionApp.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-10-30.
//

import SwiftUI
import os

@main
struct PokemonCardDetectionApp: App {
    @State private var cameraModel = CameraModel()

    var body: some Scene {
//        WindowGroup {
//            CameraView(cameraModel: cameraModel)
//                .statusBarHidden(true)
//                .task {
//                    // Start the capture pipeline.
//                    await cameraModel.start()
//            }
//        }
        WindowGroup {
            AppView(cameraModel: cameraModel)
        }
    }
}


// Global logger for app
let logger = Logger()
