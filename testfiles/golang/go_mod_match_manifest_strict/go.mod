module example.com/match-test-strict

go 1.19

require (
	github.com/gin-gonic/gin v1.7.7 // Manifest declares v1.7.7 (vulnerable)
)

// Replace directive changes the resolved version
// Manifest version: v1.7.7
// Resolved version: v1.9.1 (due to replace)
// This creates a version mismatch
replace github.com/gin-gonic/gin v1.7.7 => github.com/gin-gonic/gin v1.9.1
