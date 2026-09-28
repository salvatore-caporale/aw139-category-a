#!/bin/sh
set -eu
cd "$(dirname "$0")"
SDK="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
JDK="${JAVA_HOME:-/Applications/Android Studio.app/Contents/jbr/Contents/Home}"
BT="$SDK/build-tools/36.1.0"
PLATFORM="$SDK/platforms/android-36.1/android.jar"
export JAVA_HOME="$JDK"
export PATH="$JDK/bin:$PATH"
mkdir -p build/classes build/dex dist
"$BT/aapt2" compile --dir android/res -o build/resources.zip
"$BT/aapt2" link -I "$PLATFORM" --manifest android/AndroidManifest.xml -A web -o build/base.apk build/resources.zip
"$JDK/bin/javac" -source 8 -target 8 -classpath "$PLATFORM" -d build/classes android/src/com/aw139/categorya/MainActivity.java
"$JDK/bin/jar" cf build/classes.jar -C build/classes .
"$BT/d8" --lib "$PLATFORM" --min-api 26 --output build/dex build/classes.jar
cp build/base.apk build/unsigned.apk
(cd build/dex && zip -q ../unsigned.apk classes.dex)
"$BT/zipalign" -f 4 build/unsigned.apk build/aligned.apk
if [ ! -f build/debug.keystore ]; then
 "$JDK/bin/keytool" -genkeypair -keystore build/debug.keystore -storepass android -keypass android -alias androiddebugkey -dname 'CN=AW139-Category-A Development' -keyalg RSA -validity 3650
fi
"$BT/apksigner" sign --ks build/debug.keystore --ks-pass pass:android --out dist/AW139-Category-A-v1.apk build/aligned.apk
"$BT/apksigner" verify dist/AW139-Category-A-v1.apk
