import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"

import { cn } from "@/lib/utils"

const typographyVariants = cva("", {
  variants: {
    variant: {
      h1: "text-4xl font-bold text-navy dark:text-white",
      h2: "text-2xl font-bold text-navy dark:text-white",
      h3: "text-lg font-semibold text-navy dark:text-white",
      body: "text-sm font-normal text-foreground",
      small: "text-xs font-normal text-muted-foreground",
      // Display variants
      "display-lg": "text-6xl font-bold text-navy dark:text-white",
      "display-md": "text-5xl font-bold text-navy dark:text-white",
      // Specialized variants
      "body-lg": "text-base font-normal text-foreground",
      "body-emphasis": "text-sm font-medium text-navy dark:text-white",
      caption: "text-xs font-normal text-muted-foreground",
      overline: "text-xs font-medium uppercase tracking-wider text-muted-foreground",
    },
    color: {
      default: "",
      navy: "text-navy",
      gold: "text-gold",
      cyan: "text-cyan",
      muted: "text-muted-foreground",
      error: "text-error",
      success: "text-success",
      warning: "text-warning",
      white: "text-white",
    },
    align: {
      left: "text-left",
      center: "text-center",
      right: "text-right",
      justify: "text-justify",
    },
    weight: {
      normal: "font-normal",
      medium: "font-medium",
      semibold: "font-semibold",
      bold: "font-bold",
    },
  },
  defaultVariants: {
    variant: "body",
    color: "default",
    align: "left",
  },
})

type TypographyProps<T extends React.ElementType = "p"> = {
  as?: T
  variant?: VariantProps<typeof typographyVariants>["variant"]
  color?: VariantProps<typeof typographyVariants>["color"]
  align?: VariantProps<typeof typographyVariants>["align"]
  weight?: VariantProps<typeof typographyVariants>["weight"]
  className?: string
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<T>

const Typography = <T extends React.ElementType = "p">({
  as,
  variant = "body",
  color = "default",
  align = "left",
  weight,
  className,
  children,
  ...props
}: TypographyProps<T>) => {
  const Component = as || getDefaultComponent(variant)
  
  return (
    <Component
      className={cn(
        typographyVariants({ variant, color, align, weight }),
        className
      )}
      {...props}
    >
      {children}
    </Component>
  )
}

// Helper to determine default HTML element based on variant
function getDefaultComponent(
  variant: TypographyProps["variant"]
): React.ElementType {
  switch (variant) {
    case "h1":
    case "display-lg":
    case "display-md":
      return "h1"
    case "h2":
      return "h2"
    case "h3":
      return "h3"
    case "body":
    case "body-lg":
    case "body-emphasis":
      return "p"
    case "small":
    case "caption":
    case "overline":
      return "span"
    default:
      return "p"
  }
}

// Pre-configured components for convenience
export const H1: React.FC<Omit<TypographyProps<"h1">, "variant">> = (props) => (
  <Typography as="h1" variant="h1" {...props} />
)

export const H2: React.FC<Omit<TypographyProps<"h2">, "variant">> = (props) => (
  <Typography as="h2" variant="h2" {...props} />
)

export const H3: React.FC<Omit<TypographyProps<"h3">, "variant">> = (props) => (
  <Typography as="h3" variant="h3" {...props} />
)

export const Body: React.FC<Omit<TypographyProps<"p">, "variant">> = (props) => (
  <Typography as="p" variant="body" {...props} />
)

export const Small: React.FC<Omit<TypographyProps<"span">, "variant">> = (props) => (
  <Typography as="span" variant="small" {...props} />
)

export const DisplayLarge: React.FC<Omit<TypographyProps<"h1">, "variant">> = (props) => (
  <Typography as="h1" variant="display-lg" {...props} />
)

export const DisplayMedium: React.FC<Omit<TypographyProps<"h1">, "variant">> = (props) => (
  <Typography as="h1" variant="display-md" {...props} />
)

export const Caption: React.FC<Omit<TypographyProps<"span">, "variant">> = (props) => (
  <Typography as="span" variant="caption" {...props} />
)

export const Overline: React.FC<Omit<TypographyProps<"span">, "variant">> = (props) => (
  <Typography as="span" variant="overline" {...props} />
)

export { Typography, typographyVariants }