import SwiftUI
import WebKit
@main struct CategoryAApp: App {
 var body: some Scene { WindowGroup { CalculatorView().ignoresSafeArea(.container, edges: .bottom) } }
}
struct CalculatorView: UIViewRepresentable {
 func makeUIView(context: Context) -> WKWebView {
  let config = WKWebViewConfiguration()
  config.websiteDataStore = .nonPersistent()
  let view = WKWebView(frame: .zero, configuration: config)
  view.isOpaque = false
  view.backgroundColor = UIColor(red: 0.063, green: 0.176, blue: 0.235, alpha: 1)
  if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "web") { view.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent()) }
  return view
 }
 func updateUIView(_ uiView: WKWebView, context: Context) {}
}
