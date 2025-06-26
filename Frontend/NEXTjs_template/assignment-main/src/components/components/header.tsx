import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { AlignJustify, Phone } from "lucide-react";

const Header = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered2, setIsHovered2] = useState(false);

  const handleMouseMove = (event: React.MouseEvent<HTMLButtonElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  return (
    <motion.div
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="relative w-[80%] top-0 z-50 bg-[#0D0E0F] bg-transparent backdrop-blur-md border mt-8 rounded-xl border-[#252627]"
    >
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Link href="/" className="text-2xl text-white">
            ad<span className="font-semibold">Task</span>.ai
          </Link>
        </motion.div>

        <NavigationMenu className="bp2:hidden flex">
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger className="bg-transparent data-[state=open]:bg-transparent hover:bg-transparent data-[state=open]:text-white hover:text-white">
                Products
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[600px] gap-3 p-6 bg-gradient-to-r from-[#090B0F] backdrop-blur-md to-[#171B24]  grid-cols-2">
                  <li className="col-span-1">
                    <span className="text-lg font-medium text-[#5B698B]">
                      Products
                    </span>
                    <ul className="mt-4">
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/optimize"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Optimize
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/content-analytics"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Content Analytics
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-research"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Keyword Research
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-tracking"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Keyword Tracking
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-clustering"
                            className="text-white hover:text-gray-300"
                          >
                            Keyword Clustering
                          </a>
                        </NavigationMenuLink>
                      </li>
                    </ul>
                  </li>
                  <li className="col-span-1">
                    <ul className="mt-12 space-y-4">
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/competitor-research"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Competitor Research
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/social-listening"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Social Listening
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/autodetect"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            AutoDetect
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/site-audit"
                            className="text-white hover:text-gray-300"
                          >
                            Site Audit
                          </a>
                        </NavigationMenuLink>
                      </li>
                    </ul>
                  </li>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <NavigationMenuTrigger className="bg-transparent data-[state=open]:bg-transparent hover:bg-transparent data-[state=open]:text-white hover:text-white">
                Tools
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[600px] gap-3 p-6 bg-gradient-to-r from-[#090B0F] backdrop-blur-md to-[#171B24]  grid-cols-2">
                  <li className="col-span-1">
                    <span className="text-lg font-medium text-[#5B698B]">
                      Tools
                    </span>
                    <ul className="mt-4">
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/optimize"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            SEO Title Generator
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/content-analytics"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Seo Keyword Generator
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-research"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Meta Description Generator
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-tracking"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Blog Idea generator
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/keyword-clustering"
                            className="text-white hover:text-gray-300"
                          >
                            Website ranking checker
                          </a>
                        </NavigationMenuLink>
                      </li>
                    </ul>
                  </li>
                  <li className="col-span-1">
                    <ul className="mt-12 space-y-4">
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/competitor-research"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Keyword rank checker
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="/social-listening"
                            className="text-white hover:text-gray-300 block pb-1"
                          >
                            Backlink Chekcer
                            <div className="w-[150px] h-[1px] mt-4 bg-gradient-to-r from-[#2E3A58] to-[#455783]" />
                          </a>
                        </NavigationMenuLink>
                      </li>
                    </ul>
                  </li>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem>
              <Link href="/contact" legacyBehavior passHref>
                <NavigationMenuLink className={cn("text-sm")}>
                  Contact Us
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>

        <AlignJustify className="w-6 h-6 bp3:flex hidden" />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bp3:hidden flex items-center gap-4"
        >
          <motion.button
            className="group relative overflow-hidden border-[2px] border-[#5B698B] rounded-full bg-gradient-to-b from-black to-[rgb(65,64,64)] px-8 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(0,0,0,0.30)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered1(true)}
            onHoverEnd={() => setIsHovered1(false)}
          >
            <span className="relative z-10">Log in</span>
            {isHovered1 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.15), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>

          <motion.button
            className="group relative bp1:hidden flex border-[2px] border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] px-8 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered2(true)}
            onHoverEnd={() => setIsHovered2(false)}
          >
            <span className="relative z-10">Schedule a Call</span>
            {isHovered2 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.2), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>
          <motion.button
            className="group relative bp1:flex hidden border-[2px] border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] px-8 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
            onMouseMove={handleMouseMove}
            onHoverStart={() => setIsHovered2(true)}
            onHoverEnd={() => setIsHovered2(false)}
          >
            <Phone className="relative z-10 w-6 h-6" />
            {isHovered2 && (
              <motion.div
                className="absolute inset-0 z-0"
                animate={{
                  background: [
                    `radial-gradient(40px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(255,255,255,0.2), transparent 50%)`,
                  ],
                }}
                transition={{ duration: 0.15 }}
              />
            )}
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Header;
