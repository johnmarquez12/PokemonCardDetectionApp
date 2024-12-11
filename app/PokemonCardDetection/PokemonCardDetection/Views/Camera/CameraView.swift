//
//  CameraView.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-11-26.
//

import SwiftUI
import AVFoundation

@MainActor
struct CameraView<CameraModel: Camera>: View {
    @State var cameraModel: CameraModel
    
    var body: some View {
        ZStack {
            PreviewContainer(cameraModel: cameraModel) {
                CameraPreview(source: cameraModel.previewSource)
                    .onTapGesture {
                        location in
                        Task {
                            await cameraModel.focusAndExpose(at: location)
                        }
                    }
                    .gesture(
                        MagnificationGesture()
                            .onChanged { scale in
                                Task {
                                    print("scale factor is  " + scale.description)
                                    await cameraModel.zoom(scaleFactor: scale)
                                }
                            }
                    )
                    .opacity(cameraModel.shouldFlashScreen ? 0 : 1)
            }
            CameraUI(cameraModel: cameraModel)
        }
    }
}

#Preview {
    CameraView(cameraModel: PreviewCameraModel())
}
