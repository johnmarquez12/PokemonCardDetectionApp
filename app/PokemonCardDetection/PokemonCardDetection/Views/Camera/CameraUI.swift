//
//  CameraControlsView.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-11-30.
//

import SwiftUI
import AVFoundation

struct CameraUI<CameraModel: Camera>: View {
    @State var cameraModel: CameraModel
    
    var body: some View {
        compactUI
        .overlay {
            StatusOverlayView(status: cameraModel.status)
        }
    }
    
    @ViewBuilder
    var compactUI: some View {
        VStack {
            Spacer()
            CameraControls(cameraModel: cameraModel)
                .padding(.bottom, bottomPadding)
        }
    }
    
    var bottomPadding: CGFloat {
        // Dynamically calculate the offset for the bottom toolbar in iOS.
        let bounds = UIScreen.main.bounds
        let rect = AVMakeRect(aspectRatio: photoAspectRatio, insideRect: bounds)
        return (rect.minY.rounded() / 2) 
    }
    
}
