//
//  SwitchCameraButton.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-12-01.
//

/*
See the LICENSE.txt file for this sample’s licensing information.

Abstract:
A view that displays a button to switch between available cameras.
*/

import SwiftUI

/// A view that displays a button to switch between available cameras.
struct SwitchCameraButton<CameraModel: Camera>: View {
    
    @State var cameraModel: CameraModel
    
    var body: some View {
        Button {
            Task {
                await cameraModel.switchVideoDevices()
            }
        } label: {
            Image(systemName: "arrow.triangle.2.circlepath")
        }
        .buttonStyle(DefaultButtonStyle(size: .large))
        .frame(width: largeButtonSize.width, height: largeButtonSize.height)
        .disabled(cameraModel.captureActivity.isRecording)
        .allowsHitTesting(!cameraModel.isSwitchingVideoDevices)
    }
}
