//
//  AppView.swift
//  PokemonCardDetection
//
//  Created by John Marquez on 2024-12-04.
//

import SwiftUICore
import SwiftUI

@MainActor
struct AppView: View {
    
    @State var cameraModel: CameraModel
    
    var body: some View {
        tabBarView
    }
    
    @ViewBuilder
    var tabBarView: some View {
        TabView {
            HomeView()
                .tabItem { Image(systemName: "house.fill") }
            CameraView(cameraModel: cameraModel)
                .tabItem { Image(systemName: "camera") }
                .statusBarHidden(true)
                .task {
                    await cameraModel.start()
                }
        }
        .navigationBarTitle("Pokemon Card Detection")
    }
}
