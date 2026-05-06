plugins {
    id("java")
}

group = "org.acme.mixed"
version = "1.0.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    // Production dependencies (should be scanned)
    implementation("log4j:log4j:1.2.17")                          // vulnerable
    implementation("commons-collections:commons-collections:3.2.1")  // vulnerable
    runtimeOnly("org.keycloak:keycloak-core:20.0.0")              // vulnerable (CVE-2022-3782)

    // Compile-only dependencies (should be excluded - not in runtime)
    compileOnly("org.projectlombok:lombok:1.18.24")
    compileOnly("javax.servlet:javax.servlet-api:4.0.1")

    // Test dependencies (should be excluded)
    testImplementation("junit:junit:4.12")
    testImplementation("org.springframework:spring-core:5.3.18")   // vulnerable but test-only
    testCompileOnly("org.mockito:mockito-core:4.0.0")
}

tasks.test {
    useJUnitPlatform()
}
