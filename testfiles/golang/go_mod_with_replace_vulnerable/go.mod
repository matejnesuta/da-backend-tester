module example.com/replace-test

go 1.19

require (
	github.com/gin-gonic/gin v1.7.7          // vulnerable version in require
	github.com/emicklei/go-restful/v3 v3.0.0 // vulnerable (CRITICAL)
)

// Replace vulnerable gin with patched version - scanner should analyze v1.9.1 instead
replace github.com/gin-gonic/gin v1.7.7 => github.com/gin-gonic/gin v1.9.1
