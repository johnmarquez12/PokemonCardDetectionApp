//
//  PreviewContainer.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-11-27.
//

import CoreFoundation
import SwiftUICore
import Foundation

// Portrait-orientation aspect ratios.
typealias AspectRatio = CGSize
let photoAspectRatio = AspectRatio(width: 3.0, height: 4.0)

@MainActor
struct PreviewContainer<Content: View, CameraModel: Camera>: View {
    
    @State private var blurRadius = CGFloat.zero
    @State var cameraModel: CameraModel
    
    // When running in photo capture mode on a compact device size, move the preview area
    // update by the offset amount so that it's better centered between the top and bottom bars.
    private let photoModeOffset = CGFloat(-44)
    private let content: Content
    
    init(cameraModel: CameraModel, @ViewBuilder content: () -> Content) {
        self.cameraModel = cameraModel
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            previewView
        }
        .clipped()
        // Apply an appropriate aspect ratio based on the selected capture mode.
        .aspectRatio(photoAspectRatio, contentMode: .fit)
        // In photo mode, adjust the vertical offset of the preview area to better fit the UI.
        .offset(y: photoModeOffset)
    }
    
    /// Attach animations to the camera preview.
    var previewView: some View {
        content
            .blur(radius: blurRadius, opaque: true)
            .onChange(of: cameraModel.isSwitchingModes, updateBlurRadius(_:_:))
            .onChange(of: cameraModel.isSwitchingVideoDevices, updateBlurRadius(_:_:))
    }
    
    func updateBlurRadius(_: Bool, _ isSwitching: Bool) {
        withAnimation {
            blurRadius = isSwitching ? 30 : 0
        }
    }
}
