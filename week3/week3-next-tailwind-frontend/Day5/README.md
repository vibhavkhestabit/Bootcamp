# Readme Report for Week 3: Advance Frontend (Next.js + TailwindCSS)

We will be covering the entire week day by day, so that the flow remains maintained.

We have worked on the same file/dashboard only but with each step increased its functionality;i.e.; added profile page, about page , added layout system in our project; i.e.; switching from one place to other, understanding the concept of routing;i.e,; fetching the data using {children}, from basic Tailwind utilities to advance tailwind fucntionalities we covered it all and created a full end to end fully multi page UI in next.js and Tailwind.

## Week3: Day 1- TailwindCSS + UI System Basics

So firstly we need to understand the concept of components while using tailwind and next.js becuase we started off with our journey by creating seperate components for separate entities and imported them in our page.jsx file. Before creating our page.jsx we must create a layout.jsx file which contains the entire layout of our project and which can act as the parent so that we dont need to reconfigure the same parent layout in each and every file and can be added in all just by using our {children} keyword.

- Next.js Integration: We successfully installed and initialized Tailwind CSS within the Next.js environment to enable rapid styling via utility classes
- We began by creating 2 components on day 1, the navbar and the sidebar which werent operatable right now, used flex for navbar and flex-col for sidebar to maintain them on x and y axis and practiced how to position them properly 
- Utility-First Design: We mastered the use of spacing (p-, m-), specialized colors (slate and blue palettes), and typography to create a high-fidelity interface.
- "import Sidebar from "@/components/ui/Sidebar";" Using this command at the top of our file helps us to import any component into our page.jsx/ layout.jsx whereever it is required.

![Screenshot 1](screenshots/report-ss-1.png)
![Screenshot 2](screenshots/report-ss-2.png)

## Week3: Day 2- Tailwind Advanced + Component Library

This day we worked extensively on more components so that we knew how components ar ecreated, what are props insides components, how to use those props, and how to assign values. We also worked using the useState which is a feature of react which helps us to swtich different states and set new states.

- We worked on multiple components like Badge, button, card, input, modal and worked with their props/attributes;i.e.; whenever you are using button who need to give onclick as a prop which will definitely be used in page.jsx/layout.jsx whereever we are using that button and in the same way we use onClose as a prop in modal and give its value whereever it is used in any file.
- In modal, our open is set to be display: hidden or return null, if (!open) return null;. 
- Then we have created isOpen and a new property setIsOpen which can be used only by useState, const [isOpen, setIsOpen] = useState(false); and set is as false.
- Button variant="primary" onClick={() => setIsOpen(true)}>Download Report, while calling the button on which we have applied onClick, we have used our setIsOpen and changed its property to be true which makes our Modal visible
- Modal open={isOpen} title="Report Download System" onClose={() => setIsOpen(false)}, and to close modal and set the property back to false we have paired it with onClose which helps us intregating our Modal and button components in our page.jsx
- We have also used card and different button states which are referred as variants where there are multiple of varities/options to work on. For ex. Warning, Success, Danger etc and added different colours and properties and wherever any particular varient of the button/card is needed then we just need to call that varient and not reinitialize everythign again.
- A special prop children is used which helps to fetch all the page.jsx data/ attributes which is being used in the adjacent page.jsx file.

![Screenshot 3](screenshots/badge-ss.png)
![Screenshot 4](screenshots/button-ss.png)
![Screenshot 5](screenshots/card-ss.png)
![Screenshot 6](screenshots/input-ss.png)
![Screenshot 7](screenshots/modal-ss.png)

## Week3: Day 3- Next.js Routing + Layout System





