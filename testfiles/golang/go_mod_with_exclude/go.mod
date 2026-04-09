module example.com/exclude-test

go 1.19

require (
	github.com/gin-gonic/gin v1.7.7  // vulnerable but will be auto-upgraded due to exclude
	golang.org/x/text v0.3.7         // should be included (vulnerable)
)

// Exclude the vulnerable gin version - Go should automatically select a different version
exclude github.com/gin-gonic/gin v1.7.7
