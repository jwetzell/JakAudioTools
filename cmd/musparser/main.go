package main

import (
	"context"
	"fmt"
	"os"

	"github.com/jwetzell/jakaudiotools"
	"github.com/urfave/cli/v3"
)

func main() {
	cmd := &cli.Command{
		Name:  "vagparser",
		Usage: "parse VAG files",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:     "mus",
				Value:    "",
				Usage:    "path to JAK MUS file",
				Required: true,
			},
			&cli.StringFlag{
				Name:     "output",
				Usage:    "directory to output parsed MUS files to (if not specified, will just print names and counts)",
				Value:    "",
				Required: false,
			},
		},
		Action: func(ctx context.Context, cmd *cli.Command) error {
			musPath := cmd.String("mus")
			musData, err := os.ReadFile(musPath)
			if err != nil {
				return fmt.Errorf("failed to read WAD file: %w", err)
			}

			musFile, err := jakaudiotools.ParseMUS(musData)
			if err != nil {
				return fmt.Errorf("failed to parse MUS file: %w", err)
			}

			fmt.Printf("found MUS %+v\n", musFile)

			return nil
		},
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}
