/* eslint-disable @next/next/no-html-link-for-pages */
"use client";

import { motion } from "framer-motion";

import Header from "@/components/components/header";
import {
  Gauge,
  Globe,
  Mail,
  MapPin,
  Megaphone,
  MousePointerClick,
  Phone,
  SquareDashedMousePointer,
  TrendingUpIcon,
  WandSparkles,
} from "lucide-react";
import { HoverBorderGradient } from "@/components/components/FramerButton";
import { BorderBeam } from "@/components/magicui/border-beam";
import { useState } from "react";
import LogoMarquee from "@/components/components/marquee";
import GlowingAdSenseCard from "@/components/components/Social";
import BentoGrid from "@/components/components/bento-grid";
import Grid from "@/components/components/grid";
import Grid2 from "@/components/components/grid2";

export default function Home() {
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered2, setIsHovered2] = useState(false);
  const [isHovered1, setIsHovered1] = useState(false);
  const [isHovered3, setIsHovered3] = useState(false);

  const handleMouseMove = (event: React.MouseEvent<HTMLButtonElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  return (
    <div className="relative min-h-screen w-full h-full flex flex-col items-center overflow-hidden">
      <Header />

      <main className="relative pt-32 pb-16   container mx-auto px-4 z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-6 flex flex-col gap-8 items-center justify-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-block"
          >
            <span className="relative px-4 py-2 rounded-xl flex flex-row gap-2 items-center bg-white/10 text-sm text-white/90 backdrop-blur-sm border border-white/10 overflow-hidden">
              {/* Tinted Glowing Line */}
              <motion.div
                className="absolute top-0 w-[10px] h-full bg-blue-300 opacity-60 blur-md shadow-2xl"
                initial={{ left: "-10%" }}
                animate={{ left: "110%" }}
                transition={{
                  repeat: Infinity,
                  duration: 2,
                  ease: "linear",
                }}
              />

              <WandSparkles className="w-4 h-4 relative z-10" />
              <p className="relative z-10">
                TRANSFORM YOUR DIGITAL PRESENCE WITH AI AGENTS
              </p>
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-8xl text-center bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]"
          >
            <motion.span
              className="text-[#d0d2d8] bp3:text-6xl text-8xl font-light relative flex space-x-1"
              onHoverStart={() => setIsHovered(true)}
              onHoverEnd={() => setIsHovered(false)}
            >
              {"adTask.ai".split("").map((char, index) => (
                <motion.span
                  key={index}
                  className={`inline-block ${
                    char === "T" ||
                    (char === "a" && index === 3) ||
                    char === "s" ||
                    char === "k"
                      ? "font-semibold"
                      : ""
                  }`}
                  animate={
                    isHovered
                      ? {
                          textShadow: "0px 0px 20px rgba(142, 146, 156, 1)", // Glow effect in #8E929C
                          color: "#d9dbdf", // Color change on hover
                        }
                      : {
                          textShadow: "0px 0px 0px rgba(142, 146, 156, 0)",
                          color: "white", // Default color when not hovered
                        }
                  }
                  whileHover={{ y: -5 }} // Moves letter slightly up when hovered
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                >
                  {char}
                </motion.span>
              ))}
            </motion.span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="max-w-2xl mx-auto text-[15px] text-white"
          >
            Stop struggling with marketing decisions. Our AI assistant analyzes
            your business, creates personalized strategies, and helps you
            execute them - all in real-time.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="space-y-4 flex flex-col items-center justify-center"
          >
            <HoverBorderGradient className="bg-gradient-to-b from-[rgb(91,105,139)] to-[#828282] px-6 font-extralight py-3 text-[16]">
              Start Free Trial
            </HoverBorderGradient>
            <p className="text-sm text-white/50">
              Try AdTask AI free for 30 days
            </p>
          </motion.div>
        </motion.div>
      </main>

      <div className="min-h-screen mt-32 w-full h-full flex flex-col items-center overflow-hidden relative bg-gradient-to-b from-[#040508] to-[#0C0F15]">
        <div className="w-[70%]  relative flex items-center justify-center bg-black bp4:h-[400px] bp3:h-[350px] h-[600px] rounded-2xl overflow-hidden">
          {/* Animated Border Effects */}
          <BorderBeam
            duration={6}
            size={1000}
            className="from-transparent via-red-500 to-transparent"
          />
          <BorderBeam
            duration={6}
            delay={3}
            size={1000}
            className="from-transparent via-blue-500 to-transparent"
          />
          <BorderBeam
            duration={6}
            size={1000}
            className="from-transparent via-red-500 to-transparent"
          />
          <BorderBeam
            duration={6}
            delay={3}
            size={1000}
            className="from-transparent via-blue-500 to-transparent"
          />

          {/* Text (Behind YouTube Logo) */}
          <motion.span
            className="text-white bp4:text-5xl text-9xl font-light absolute z-0"
            initial={{ textShadow: "0px 0px 0px rgba(91, 105, 139, 0)" }}
            whileHover={{
              textShadow: [
                "0px 0px 5px rgba(91, 105, 139, 0.5)",
                "0px 0px 15px rgba(91, 105, 139, 0.7)",
                "0px 0px 25px rgba(91, 105, 139, 1)",
                "0px 0px 40px rgba(91, 105, 139, 1)",
                "0px 0px 60px rgba(91, 105, 139, 1)",
              ],
              scale: 1.12,
              transition: { duration: 0.2, ease: "easeInOut" },
            }}
          >
            ad<span className="font-semibold">Task</span>.ai
          </motion.span>

          {/* YouTube Icon (Centered & On Top) */}
          <div className="absolute inset-0 flex items-center justify-center z-10 bg-black/40 ">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              id="Youtube"
              className="w-[16%] h-[16%] bp3:h-[8%] bp3:w-[8%] "
            >
              <g
                fillRule="evenodd"
                clipRule="evenodd"
                fill="#130101"
                className="color000000 svgShape"
              >
                <path
                  fill="#f43636"
                  d="M15.32 4.06c-.434-.772-.905-.914-1.864-.968C12.498 3.027 10.089 3 8.002 3c-2.091 0-4.501.027-5.458.091-.957.055-1.429.196-1.867.969C.23 4.831 0 6.159 0 8.497v.008c0 2.328.23 3.666.677 4.429.438.772.909.912 1.866.977.958.056 3.368.089 5.459.089 2.087 0 4.496-.033 5.455-.088.959-.065 1.43-.205 1.864-.977.451-.763.679-2.101.679-4.429v-.008c0-2.339-.228-3.667-.68-4.438z"
                  className="colorf44336 svgShape"
                ></path>
                <path
                  fill="#fafafa"
                  d="M6 11.5v-6l5 3z"
                  className="colorfafafa svgShape"
                ></path>
              </g>
            </svg>
          </div>
        </div>

        <div className="w-full mt-8">
          <LogoMarquee />
        </div>
      </div>

      <div className="min-h-screen w-full h-full flex flex-col z-0 items-center relative bg-gradient-to-b from-[#0C0F15] to-[#0C0F16]">
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute left-1/2 top-[20px] -translate-x-1/2 w-[700px] h-[700px] bg-grid-black/[0.9] dark:bg-grid-white/[0.05] bg-[length:50px_50px]"
            style={{
              maskImage:
                "radial-gradient(circle, rgba(0,0,0,1) 20%, rgba(0,0,0,0) 60%)",
              WebkitMaskImage:
                "radial-gradient(circle, rgba(0,0,0,1) 20%, rgba(0,0,0,0) 60%)",
            }}
          />

          <div className="flex flex-col justify-center mt-14 items-center w-full">
            <p className="text-[16px] text-gray-200">Adtask AI works with: </p>
            <GlowingAdSenseCard />
          </div>
        </div>

        <div className="flex mt-96 flex-col bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Button */}
          <div className="flex justify-center text-center bp1:mt-32 bp4:mt-44 mt-0 z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Features</span>
            </HoverBorderGradient>
          </div>

          {/* Text & Gradient Borders */}
          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              {/* Outer Soft Glow - Larger Ellipse */}
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />

              {/* Inner Glow - Smaller & Brighter Ellipse */}
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>
            {/* First Line */}
            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Feature packed to Make
            </p>

            {/* Borders (Shifted Further Left & Right) */}
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[30%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[30%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>

            {/* Second Line */}
            <p className="text-5xl  bp4:text-3xl bp3:text-xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              Digital marketing easier and affordable
            </p>
          </div>

          <BentoGrid />
        </div>
        <div className="flex bp6:-mt-48 -mt-24 flex-col bg-transparent bg-gradient-to-b to-[#040508] from-[#0C0F15] justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Button */}
          <div className="flex justify-center text-center z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Services</span>
            </HoverBorderGradient>
          </div>

          {/* Text & Gradient Borders */}
          <div className="w-[70%] flex flex-col mt-8 items-center justify-center relative z-10">
            {/* First Line */}
            <p className=" text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Innovative Services
            </p>

            {/* Borders (Shifted Further Left & Right) */}
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[40%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[40%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>

            {/* Second Line */}
            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              For Growth
            </p>
          </div>

          <div className="grid grid-cols-3 bp1:grid-cols-2 bp6:grid-cols-1 mt-14 gap-0 mb-10">
            <Grid
              title={"Smart Ad Targeting"}
              text={
                "AI-powered audience segmentation ensures your ads reach the right people, delivering higher ROI and maximum conversion rates."
              }
            >
              <MousePointerClick className="w-20 h-20" />
            </Grid>
            <Grid
              title={"Performance Analytics"}
              text={
                "Access real-time insights and track key metrics across all campaigns in one unified dashboard to quickly refine your strategies.."
              }
            >
              <Gauge className="w-20 h-20" />
            </Grid>
            <Grid
              title={"SEO Automation"}
              text={
                "Automate keyword research and content optimization suggestions to improve your search engine rankings with less effort."
              }
            >
              <TrendingUpIcon className="w-20 h-20" />
            </Grid>
            <Grid
              title={"Social Media Marketing"}
              text={
                "AI agents craft personalized content, schedule posts, monitor engagement, and refine strategies in real time for maximum impact."
              }
            >
              <Globe className="w-20 h-20" />
            </Grid>
            <Grid
              title={"Conversion Optimization"}
              text={
                "AI-driven A/B testing and automated tweaks to landing pages and funnels help you consistently improve conversion rates."
              }
            >
              <SquareDashedMousePointer className="w-20 h-20" />
            </Grid>
            <Grid
              title={"Campaign Automation"}
              text={
                "Centralize and streamline your ad management. Our intelligent engine automatically adjusts bids, budgets, and targeting to maximize results."
              }
            >
              <Megaphone className="w-20 h-20" />
            </Grid>
          </div>

          <div className="flex justify-center text-center bg-gradient-to-b from-[#040508] to-[#0C0F15] z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black border-[1px] border-[#5A678A] bg-white text-black dark:text-white flex items-center space-x-2"
              style={{ background: "linear-gradient(to bottom, black, white)" }}
            >
              <span className="text-xl font-light">Contact us</span>
            </HoverBorderGradient>
          </div>
        </div>
        <div className="flex pt-32 flex-col bg-gradient-to-b from-[#040508] to-[#0C0F15] bg-transparent justify-center items-center w-full relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Button */}
          <div className="flex justify-center text-center z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Services</span>
            </HoverBorderGradient>
          </div>

          {/* Text & Gradient Borders */}
          <div className="w-[70%] flex flex-col mt-7  items-center justify-center relative z-10">
            <div className="absolute inset-x-0 top-[-50px] z-0 flex justify-center">
              {/* Outer Soft Glow - Larger Ellipse */}
              <div
                className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                style={{ borderRadius: "50%" }}
              />

              {/* Inner Glow - Smaller & Brighter Ellipse */}
              <div
                className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                style={{ borderRadius: "50%" }}
              />
            </div>
            {/* First Line */}
            <p className=" text-5xl bp3:text-xl bp4:text-3xl text-center font-light">
              Trusted By
            </p>

            {/* Borders (Shifted Further Left & Right) */}
            <div className="relative flex items-center w-full justify-center mt-1">
              <div className="absolute -left-40 h-[1px] w-[50%] bg-gradient-to-l to-black from-[#8096D2]"></div>
              <div className="absolute -right-40 h-[1px] w-[50%] bg-gradient-to-r to-black from-[#8096D2]"></div>
            </div>

            {/* Second Line */}
            <p className="text-5xl bp3:text-xl bp4:text-3xl text-center mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
              Satisfies Clients
            </p>
          </div>

          <p className="text-sm font-light mt-8">
            Discover how we&lsquo;ve driven growth and innovation
          </p>

          <div className="grid grid-cols-3 bp1:grid-cols-2 bp6:grid-cols-1 mt-14 gap-4 mb-10">
            <Grid2
              text="We used to struggle with consistent branding across platforms. adTask’s unified dashboard ensures our message stays on point every single time"
              name="Brand Director at a Tech Startup"
            />
            <Grid2
              text="Unlock actionable data to guide every decision. Stay ahead of trends, refine your strategies, and make confident moves with powerful analytics."
              name="Digital Strategist at a SaaS Company"
            />
            <Grid2
              text="adTask turned our complicated campaigns into a breeze. The built-in AI agents helped us reach exactly the customers we wanted—without guesswork!"
              name="Head of Growth at a Tech Startup"
            />
            <Grid2
              text="adTask made everything from campaign setup to performance tracking simple. Our team can now focus on creating great content rather than crunching numbers."
              name="Social Media Lead at a Non-Profit Organization"
            />
            <Grid2
              text="We've tried other platforms before, but none delivered the depth of insights adTask offers. Our conversion rates are up by 35% since we signed on!"
              name="Ecommerce Manager at a Home Décor Brand"
            />
            <Grid2
              text="We've seen a 50% boost in engagement across our social channels since switching to adTask. Its AI-driven insights are game-changing!"
              name=" Social Media Manager at a Fitness Brand"
            />
          </div>
        </div>
        <div className="flex w-full mt-32 flex-col bg-gradient-to-b to-[#040508] from-[#0C0F15] bg-transparent justify-center items-center relative">
          {/* Gradient Circle Background */}
          <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-gradient-radial from-[#293249] to-transparent opacity-40 blur-3xl"></div>

          {/* Button */}
          <div className="flex justify-center text-center z-10">
            <HoverBorderGradient
              containerClassName="rounded-full"
              as="button"
              className="dark:bg-black bg-white text-black dark:text-white flex items-center space-x-2"
            >
              <span>Contact us</span>
            </HoverBorderGradient>
          </div>
          <div className="w-[80%] mt-10  mb-10 gap-20 flex bp7:flex-col flex-row items-center justify-evenly">
            <div className="flex  flex-col relative ">
              <div className="absolute inset-x-0 top-[-50px] z-0 flex  justify-center">
                {/* Outer Soft Glow - Larger Ellipse */}
                <div
                  className="absolute w-[400px] h-[200px] bg-[#5B698B]/40 opacity-80 blur-[80px]"
                  style={{ borderRadius: "50%" }}
                />

                {/* Inner Glow - Smaller & Brighter Ellipse */}
                <div
                  className="absolute w-[300px] h-[150px] bg-[#5B698B]/50 opacity-80 blur-[100px]"
                  style={{ borderRadius: "50%" }}
                />
              </div>

              <p className="text-4xl font-light">Ask whatever you have</p>
              <p className="text-4xl bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent font-light leading-tight">
                In your Mind now
              </p>
              <p className="font-light text-sm mt-8">
                Whether you have question or are ready to discuss your
              </p>
              <p className="font-light text-sm">
                business, we&apos;re here to help reach out today!
              </p>

              <div className="mt-8 flex flex-row gap-3 items-end">
                <Mail className="w-6 h-6 text-[#8096D2]" />
                <p className="font-light  text-sm">contact@adtask.ai</p>
              </div>
              <div className="mt-8 flex flex-row gap-3 items-end">
                <Phone className="w-6 h-6 text-[#8096D2]" />
                <p className="font-light  text-sm">(969) 819 8061</p>
              </div>
              <div className="mt-8 flex flex-row gap-3 items-end">
                <MapPin className="w-6 h-6 text-[#8096D2]" />
                <p className="font-light  text-sm">San Fransisco bay Area</p>
              </div>

              <div className="bp7:flex mt-8 hidden flex-col ">
                <p className="font-light text-sm">Name</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[35px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>
              <div className=" bp7:flex mt-8 hidden flex-col">
                <p className="font-light text-sm">Email</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[35px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>
              <div className=" bp7:flex  mt-8 hidden flex-col">
                <p className="font-light text-sm">Message</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[100px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>
            </div>

            <div className="flex bp7:hidden  gap-4 flex-col  ">
              <div className="flex flex-col">
                <p className="font-light text-sm">Name</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[35px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>
              <div className="flex flex-col">
                <p className="font-light text-sm">Email</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[35px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>
              <div className="flex flex-col">
                <p className="font-light text-sm">Message</p>
                <input
                  className="w-[500px] bp7:w-[350px] text-sm pl-3 bg-transparent border-[1px] mt-2 h-[100px] text-white border-[#333B4F] rounded-md focus:outline-none focus:border-[#8096D2]"
                  style={{ zIndex: 50, position: "relative" }}
                />
              </div>

              <motion.button
                className="group relative w-[100px] border-[2px] border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] px-2 py-2 text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
                onMouseMove={handleMouseMove}
                onHoverStart={() => setIsHovered2(true)}
                onHoverEnd={() => setIsHovered2(false)}
              >
                <span className="relative z-10">Submit</span>
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
            </div>
          </div>
        </div>

        <div className="flex w-full pt-32 flex-col bg-gradient-to-b from-[#040508] to-[#0C0F15] bg-transparent justify-center items-center relative">
          <div className="absolute inset-x-0 top-[-120px] z-0 flex justify-center">
            {/* Larger Soft Ambient Glow */}
            <div
              className="w-0 h-0
                border-l-[300px] border-l-transparent
                border-r-[300px] border-r-transparent
                border-b-[600px] border-b-[#5B698B]/40
                blur-[100px]
                opacity-50"
            />

            {/* Inner Glow for More Softness */}
            <div
              className="absolute top-[80px]
                w-0 h-0
                border-l-[300px] border-l-transparent
                border-r-[300px] border-r-transparent
                border-b-[600px] border-b-[#5B698B]/50
                blur-[120px]
                opacity-80"
            />
          </div>

          <div className="absolute inset-0 pointer-events-none">
            <div
              className="absolute left-1/2 top-[20px] -translate-x-1/2 w-[700px] h-[700px] bg-grid-black/[0.15] dark:bg-grid-white/[0.2] bg-[length:50px_50px]"
              style={{
                maskImage:
                  "radial-gradient(circle, rgba(0,0,0,1) 20%, rgba(0,0,0,0) 60%)",
                WebkitMaskImage:
                  "radial-gradient(circle, rgba(0,0,0,1) 20%, rgba(0,0,0,0) 60%)",
              }}
            />
          </div>
          <motion.h1
            initial={{ opacity: 0.3 }}
            animate={{ opacity: 0.3 }}
            transition={{ delay: 0.4 }}
            className="text-8xl text-center bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50 drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]"
          >
            <motion.span
              className="text-[#d0d2d8] bp6:text-5xl  text-8xl font-light relative flex space-x-1"
              onHoverStart={() => setIsHovered(true)}
              onHoverEnd={() => setIsHovered(false)}
            >
              {"adTask.ai".split("").map((char, index) => (
                <motion.span
                  key={index}
                  className={`inline-block ${
                    char === "T" ||
                    (char === "a" && index === 3) ||
                    char === "s" ||
                    char === "k"
                      ? "font-semibold"
                      : ""
                  }`}
                  animate={
                    isHovered
                      ? {
                          textShadow: "0px 0px 20px rgba(142, 146, 156, 1)", // Glow effect in #8E929C
                          color: "#d9dbdf", // Color change on hover
                        }
                      : {
                          textShadow: "0px 0px 0px rgba(142, 146, 156, 0)",
                          color: "white", // Default color when not hovered
                        }
                  }
                  whileHover={{ y: -5 }} // Moves letter slightly up when hovered
                  transition={{ duration: 0.2, ease: "easeInOut" }}
                >
                  {char}
                </motion.span>
              ))}
            </motion.span>
          </motion.h1>

          <div className="w-[70%] flex flex-col mt-16 items-center justify-center relative z-10">
            {/* First Line */}
            <p className="text-5xl text-center bp6:text-3xl">
              Are you ready to boost
            </p>

            {/* Second Line */}
            <p className="text-5xl text-center bp6:text-3xl mt-2 bg-gradient-to-b from-[#8096D2] to-[#b7b9be] bg-clip-text text-transparent leading-tight">
              your Digital Presence ?
            </p>
          </div>

          <div className="flex mt-14 flex-col gap-8 items-center w-full justify-center">
            <motion.button
              className="group relative font-light overflow-hidden border-[2px] border-[#5B698B] rounded-full bg-gradient-to-b from-black to-[rgb(65,64,64)] h-[43px] w-[191px] text-white backdrop-blur-sm transition-colors hover:bg-[rgba(0,0,0,0.30)]"
              onMouseMove={handleMouseMove}
              onHoverStart={() => setIsHovered1(true)}
              onHoverEnd={() => setIsHovered1(false)}
            >
              <span className="relative z-10">Start Free Trial</span>
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
              className="group relative border-[2px] font-light border-[#5B698B] overflow-hidden rounded-full bg-gradient-to-b from-[rgb(91,105,139)] to-[#414040] h-[43px] w-[191px] text-white backdrop-blur-sm transition-colors hover:bg-[rgba(255,255,255,0.2)]"
              onMouseMove={handleMouseMove}
              onHoverStart={() => setIsHovered3(true)}
              onHoverEnd={() => setIsHovered3(false)}
            >
              <span className="relative z-10">Schedule a Call</span>
              {isHovered3 && (
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
          </div>
          <div className="border-t-[#333B4F] w-[90%] border-[1px] mt-10 "></div>
          <footer className="w-full flex flex-row justify-center items-center py-10">
            <div className="flex flex-row w-[90%] justify-evenly bp2:flex-col-reverse bp2:items-center bp2:gap-8">
              {/* Brand and Contact Info */}
              <div className="flex flex-col items-center gap-4">
                <h2 className="text-[#C5CDE3] bp3:text-5xl text-7xl font-light">
                  ad<span className="font-bold">Task</span>.ai
                </h2>
                <div className="flex flex-row gap-3 items-end">
                  <Mail className="w-4 h-4 text-[#8096D2]" />
                  <a
                    href="mailto:contact@adtask.ai"
                    className="font-light text-[#C5CDE3] hover:text-[#8096D2] transition-colors underline text-sm"
                  >
                    contact@adtask.ai
                  </a>
                </div>
                <div className="flex flex-row gap-3 items-end">
                  <MapPin className="w-4 h-4 text-[#8096D2]" />
                  <p className="font-light text-[#C5CDE3] text-sm">
                    San Francisco bay area
                  </p>
                </div>
              </div>

              {/* Utilities and Socials Container */}
              <div className="flex flex-row gap-16 bp3:flex-col bp3:gap-8">
                {/* Utilities Section */}
                <div>
                  <h3 className="text-[#C5CDE3] text-2xl font-bold mb-4">
                    Utilities
                  </h3>
                  <nav className="flex flex-col text-gray-400 gap-1 items-center">
                    <a
                      href="/"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Home
                    </a>
                    <a
                      href="/product"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Product
                    </a>
                    <a
                      href="/tools"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Tools
                    </a>
                    <a
                      href="/contact"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Contact Us
                    </a>
                  </nav>
                </div>

                {/* Socials Section */}
                <div>
                  <h3 className="text-[#C5CDE3] text-2xl font-bold mb-4">
                    Socials
                  </h3>
                  <nav className="flex flex-col text-gray-400 gap-1 items-center">
                    <a
                      href="#"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      X
                    </a>
                    <a
                      href="#"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      LinkedIn
                    </a>
                    <a
                      href="#"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Instagram
                    </a>
                    <a
                      href="#"
                      className="hover:text-[#8096D2] transition-colors"
                    >
                      Facebook
                    </a>
                  </nav>
                </div>
              </div>
            </div>
          </footer>
        </div>

        <div className="w-full flex justify-center text-gray-400 text-sm font-light mb-3 items-center">
          <p>All right reserved &copy; 2025 addTask</p>
        </div>
      </div>
    </div>
  );
}
