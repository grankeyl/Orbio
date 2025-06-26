import { FC } from "react"
import { Outlet } from "react-router-dom"

import Header from "@/components/Header/Header"
import Menu from "@/components/Menu/Menu"

const Layout: FC = () => {
  return (
    <div className="containered flex flex-col min-h-screen">
      <Header />
      <Outlet />
      <Menu />
    </div>
  )
}

export default Layout