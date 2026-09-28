package com.aw139.categorya;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.*;
import java.io.ByteArrayInputStream;
import java.util.Collections;
public class MainActivity extends Activity {
 private WebView web;
 @Override public void onCreate(Bundle state){super.onCreate(state);web=new WebView(this);setContentView(web);
  web.setOnApplyWindowInsetsListener((view,insets)->{view.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets;});
  web.getSettings().setJavaScriptEnabled(true);web.getSettings().setAllowFileAccess(false);web.getSettings().setAllowContentAccess(false);web.getSettings().setDomStorageEnabled(false);web.getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView w,WebResourceRequest r){
    try{if(!"https".equals(r.getUrl().getScheme())||!"aw139.local".equals(r.getUrl().getHost()))throw new Exception();
     String p=r.getUrl().getPath();if("/".equals(p))p="/index.html";
     if(!p.matches("/(?:[a-z0-9-]+\\.(?:html|js|webmanifest)|icons/[a-z0-9-]+\\.png|charts/p[0-9]+\\.webp)"))throw new Exception();
     String mime=p.endsWith(".js")?"application/javascript":p.endsWith(".webp")?"image/webp":p.endsWith(".png")?"image/png":p.endsWith(".webmanifest")?"application/manifest+json":"text/html";
     return new WebResourceResponse(mime,"UTF-8",getAssets().open(p.substring(1)));
    }catch(Exception e){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));}
   }
   @Override public boolean shouldOverrideUrlLoading(WebView w,WebResourceRequest r){return !"aw139.local".equals(r.getUrl().getHost());}
  });web.loadUrl("https://aw139.local/");
 }
 @Override public void onBackPressed(){web.evaluateJavascript("(()=>{const d=document.querySelector('dialog[open]');if(d){d.close();return true;}return false;})()",result->{if(!"true".equals(result))MainActivity.super.onBackPressed();});}
 @Override protected void onDestroy(){if(web!=null)web.destroy();super.onDestroy();}
}
