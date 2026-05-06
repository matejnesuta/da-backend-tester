module example.com/exclude-test

go 1.19

require (
	github.com/gin-gonic/gin v1.8.1  // using a newer, non-excluded version
	golang.org/x/text v0.3.7         // should be included (vulnerable)
)

// Exclude the vulnerable gin version - Go should skip this specific version
exclude github.com/gin-gonic/gin v1.7.7
