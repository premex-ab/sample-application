plugins {
    id("com.android.application")
}

android {
    namespace = "com.premexab.sample"
    compileSdk = 33

    defaultConfig {
        applicationId = "com.premexab.sample"
        minSdk = 21
        targetSdk = 33
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}
