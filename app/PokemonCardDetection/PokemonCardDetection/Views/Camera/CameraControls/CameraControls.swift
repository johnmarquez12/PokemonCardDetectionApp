//
//  CameraControls.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-11-30.
//

import SwiftUICore

struct CameraControls<CameraModel: Camera>: View {
    @State var cameraModel: CameraModel
    
    var body: some View {
        HStack {
            ThumbnailButton(cameraModel: cameraModel)
            Spacer()
            CaptureButton(cameraModel: cameraModel)
            Spacer()
            SwitchCameraButton(cameraModel: cameraModel)
        }
    }
}
