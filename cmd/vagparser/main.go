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
				Name:     "wad",
				Value:    "",
				Usage:    "path to JAK VAGWAD file",
				Required: true,
			},
			&cli.StringFlag{
				Name:     "dict",
				Value:    "",
				Usage:    "path to JAK VAGDIR file to lookup names",
				Required: true,
			},
			&cli.Int8Flag{
				Name:  "game",
				Value: 1,
				Usage: "the JAK game the VAG file is from (1,2,3)",
				Validator: func(flag int8) error {
					if flag != 1 && flag != 2 && flag != 3 {
						return fmt.Errorf("game must be either 1, 2, or 3")
					}
					return nil
				},
				Required: true,
			},
			&cli.StringFlag{
				Name:     "output",
				Usage:    "directory to output parsed VAG files to (if not specified, will just print names and counts)",
				Value:    "",
				Required: false,
			},
		},
		Action: func(ctx context.Context, cmd *cli.Command) error {
			wadPath := cmd.String("wad")
			wadData, err := os.ReadFile(wadPath)
			if err != nil {
				return fmt.Errorf("failed to read WAD file: %w", err)
			}

			dirPath := cmd.String("dict")
			dirData, err := os.ReadFile(dirPath)
			if err != nil {
				return fmt.Errorf("failed to read dict file: %w", err)
			}

			game := cmd.Int8("game")

			entries, err := jakaudiotools.ParseVAG(wadData, dirData, game)
			if err != nil {
				return fmt.Errorf("failed to parse VAG file: %w", err)
			}

			outputPath := cmd.String("output")
			if outputPath != "" {
				if _, err := os.Stat(outputPath); os.IsNotExist(err) {
					err := os.MkdirAll(outputPath, 0755)
					if err != nil {
						return fmt.Errorf("failed to create output directory: %w", err)
					}
				}
				for _, entry := range entries {
					entryPath := fmt.Sprintf("%s/%s.VAGp", outputPath, entry.Name)
					fmt.Printf("writing VAG file to %s\n", entryPath)
					err := os.WriteFile(entryPath, entry.Data, 0644)
					if err != nil {
						return fmt.Errorf("failed to write VAG file: %w", err)
					}
				}
				fmt.Printf("wrote %d VAG files to %s\n", len(entries), outputPath)
			} else {
				for _, entry := range entries {
					fmt.Printf("VAG file named %s found\n", entry.Name)
				}
				fmt.Printf("found %d VAG entries\n", len(entries))
			}
			return nil
		},
	}

	if err := cmd.Run(context.Background(), os.Args); err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}
}
