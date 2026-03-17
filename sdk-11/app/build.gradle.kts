plugins {
    id("com.android.application")
}

android {
    namespace = "com.premexab.sample"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.premexab.sample"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
