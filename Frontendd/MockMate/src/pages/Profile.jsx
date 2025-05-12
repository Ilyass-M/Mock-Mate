"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../context/AuthContext"
import axios from "axios"

const Profile = () => {

    const { user } = useAuth()

    const [profileData, setProfileData] = useState({
        email: "",
        username: "",
        fullname: "",
        phone_number: "",
        bio: "",
        avatar: "",
        skills: [],
        is_candidate: false,
        is_recruiter: false,
    })
    const [isEditing, setIsEditing] = useState(false)
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(null)
    const [newSkill, setNewSkill] = useState({ name: "", level: 50 })


    const url = "http://localhost:8000"
    const get_user_data = async () => {
        try {
            const response = await axios.get(url + "/api/user/", { withCredentials: true })
            const skills = await axios.get(url + "/api/skills/", { withCredentials: true })
            console.log("User data fetched successfully:", response.data)
            console.log(skills)
            response.data.skills = skills.data
            return  response.data 
        }
        catch (error) {
            console.error("Error fetching user data:", error)
            return null
        }
    }
    useEffect(() => {
        get_user_data().then((data) => {
            if (data) {
                setProfileData({
                    email: data.email || "",
                    username: data.username || "",
                    fullname: data.fullname || "",
                    phone_number: data.phone_number || "",
                    is_candidate: data.is_candidate || false,
                    is_recruiter: data.is_recruiter || false,
                    bio: data.bio || "Frontend developer passionate about creating beautiful user experiences.",
                    avatar: data.avatar || "/placeholder.svg?height=200&width=200",
                    skills: data.skills || [
                        { name: "React", level: 90 },
                        { name: "JavaScript", level: 85 },
                        { name: "CSS", level: 75 },
                        { name: "Node.js", level: 65 },
                    ],
                })
            }
        })

    }, [])

    const handleInputChange = (e) => {
        const { name, value } = e.target
        setProfileData((prevData) => ({
            ...prevData,
            [name]: value,
        }))
    }
    const handleSave = async () => {
        try {
            console.log("Saving profile data:", profileData)
            setError(null)
            setSuccess(null)

            // Send the data directly, not wrapped in an object
            const resp = await axios.patch(url + "/api/user/", profileData, { withCredentials: true })

            if (resp.status !== 200) {
                throw new Error("Failed to update profile")
            }

            console.log("Update response:", resp.data)
            setSuccess("Profile updated successfully!")
            setIsEditing(false)

            // Refresh user data after saving
            const data = await get_user_data()
            if (data) {
                setProfileData({
                    email: data.email || "",
                    username: data.username || "",
                    fullname: data.fullname || "",
                    phone_number: data.phone_number || "",
                    is_candidate: data.is_candidate || false,
                    is_recruiter: data.is_recruiter || false,
                    bio: data.bio || "Frontend developer passionate about creating beautiful user experiences.",
                    avatar: data.avatar || "/placeholder.svg?height=200&width=200",
                    skills: data.skills || [
                        { name: "React", level: 90 },
                        { name: "JavaScript", level: 85 },
                        { name: "CSS", level: 75 },
                        { name: "Node.js", level: 65 },
                    ],
                })
            }
        } catch (e) {
            console.error("Error updating profile:", e)
            setError("Failed to update profile. Please try again.")
        }
    }

    const handleAvatarChange = (e) => {
        const file = e.target.files[0]
        if (file) {
            const reader = new FileReader()
            reader.onloadend = () => {
                setProfileData((prevData) => ({
                    ...prevData,
                    avatar: reader.result,
                }))
            }
            reader.readAsDataURL(file)
        }
    }

    const addSkill = () => {
        if (newSkill.name.trim()) {
            setProfileData((prevData) => ({
                ...prevData,
                skills: [...prevData.skills, { ...newSkill }],
            }))
            setNewSkill({ name: "", level: 50 })
        }
    }

    const removeSkill = (index) => {
        setProfileData((prevData) => ({
            ...prevData,
            skills: prevData.skills.filter((_, i) => i !== index),
        }))
    }

    const handleSkillLevelChange = (index, level) => {
        const updatedSkills = [...profileData.skills]
        updatedSkills[index].level = level
        setProfileData((prevData) => ({
            ...prevData,
            skills: updatedSkills,
        }))
    }
    if (!user) {
        return <div className="text-center text-gray-500">Please log in to view your profile.</div>
    }
    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Left Column - Profile Picture & Basic Info */}
                    <div className="md:col-span-1">
                        <div className="bg-white rounded-lg shadow-md overflow-hidden">
                            <div className="relative bg-gradient-to-r from-purple-500 to-indigo-600 h-32">
                                {isEditing && (
                                    <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                                        <button className="px-3 py-1 bg-white text-gray-800 text-sm rounded-md hover:bg-gray-100 transition-colors">
                                            Change Cover
                                        </button>
                                    </div>
                                )}
                            </div>

                            <div className="flex justify-center -mt-16 relative">
                                <div className="relative">
                                    <div className="h-32 w-32 rounded-full border-4 border-white shadow-lg overflow-hidden bg-gray-100">
                                        {profileData.avatar ? (
                                            <img
                                                src={profileData.avatar || "/placeholder.svg"}
                                                alt={profileData.fullname}
                                                className="h-full w-full object-cover"
                                            />
                                        ) : (
                                            <div className="h-full w-full flex items-center justify-center bg-indigo-100 text-indigo-600 text-2xl font-bold">
                                                {profileData.fullname
                                                    ?.split(" ")
                                                    .map((n) => n[0])
                                                    .join("") || "U"}
                                            </div>
                                        )}
                                    </div>

                                    {isEditing && (
                                        <label
                                            htmlFor="avatar-upload"
                                            className="absolute bottom-0 right-0 bg-indigo-600 text-white p-2 rounded-full cursor-pointer shadow-md hover:bg-indigo-700 transition-colors"
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                width="16"
                                                height="16"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            >
                                                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path>
                                                <circle cx="12" cy="13" r="3"></circle>
                                            </svg>
                                            <input
                                                id="avatar-upload"
                                                type="file"
                                                accept="image/*"
                                                className="hidden"
                                                onChange={handleAvatarChange}
                                            />
                                        </label>
                                    )}
                                </div>
                            </div>

                            <div className="text-center pt-2 px-4 pb-4">
                                <h2 className="text-xl font-bold text-gray-800">{profileData.fullname || "Your Name"}</h2>
                                <p className="text-sm text-gray-500">@{profileData.username || "username"}</p>

                                <div className="mt-6 space-y-4">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Bio</h3>
                                        {isEditing ? (
                                            <textarea
                                                name="bio"
                                                value={profileData.bio || ""}
                                                onChange={handleInputChange}
                                                rows={3}
                                                className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                                            />
                                        ) : (
                                            <p className="mt-1 text-sm text-gray-700">{profileData.bio}</p>
                                        )}
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-medium text-gray-500">Contact</h3>
                                        <p className="mt-1 text-sm text-gray-700">{profileData.email}</p>
                                        <p className="mt-1 text-sm text-gray-700">{profileData.phone_number || "No phone number"}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Column - Profile Details & Skills */}
                    <div className="md:col-span-2">
                        {error && (
                            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">{error}</div>
                        )}

                        {success && (
                            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
                                {success}
                            </div>
                        )}

                        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-lg font-bold text-gray-800">Profile Information</h2>
                                {!isEditing ? (
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="px-3 py-1 border border-gray-300 rounded-md text-sm flex items-center gap-1 hover:bg-gray-50 transition-colors"
                                    >
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            width="16"
                                            height="16"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                        >
                                            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                                        </svg>
                                        Edit
                                    </button>
                                ) : (
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setIsEditing(false)}
                                            className="px-3 py-1 border border-gray-300 rounded-md text-sm flex items-center gap-1 hover:bg-gray-50 transition-colors"
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                width="16"
                                                height="16"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            >
                                                <circle cx="12" cy="12" r="10"></circle>
                                                <line x1="15" y1="9" x2="9" y2="15"></line>
                                                <line x1="9" y1="9" x2="15" y2="15"></line>
                                            </svg>
                                            Cancel
                                        </button>
                                        <button
                                            onClick={handleSave}
                                            className="px-3 py-1 bg-indigo-600 text-white rounded-md text-sm flex items-center gap-1 hover:bg-indigo-700 transition-colors"
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                width="16"
                                                height="16"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            >
                                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                                                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                                                <polyline points="7 3 7 8 15 8"></polyline>
                                            </svg>
                                            Save
                                        </button>
                                    </div>
                                )}
                            </div>

                            <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label htmlFor="fullname" className="block text-sm font-medium text-gray-700 mb-1">
                                            Full Name
                                        </label>
                                        <input
                                            id="fullname"
                                            name="fullname"
                                            value={profileData.fullname || ""}
                                            onChange={handleInputChange}
                                            disabled={!isEditing}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                                            Username
                                        </label>
                                        <input
                                            id="username"
                                            name="username"
                                            value={profileData.username || ""}
                                            onChange={handleInputChange}
                                            disabled={!isEditing}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                                            Email
                                        </label>
                                        <input
                                            id="email"
                                            name="email"
                                            type="email"
                                            value={profileData.email || ""}
                                            onChange={handleInputChange}
                                            disabled={!isEditing}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-1">
                                            Phone Number
                                        </label>
                                        <input
                                            id="phone_number"
                                            name="phone_number"
                                            value={profileData.phone_number || ""}
                                            onChange={handleInputChange}
                                            disabled={!isEditing}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-md p-6">
                            <div className="mb-4">
                                <h2 className="text-lg font-bold text-gray-800">Skills</h2>
                                <p className="text-sm text-gray-500">Your professional skills and expertise</p>
                            </div>

                            <div className="space-y-4">
                                {profileData.skills.map((skill, index) => (
                                    <div key={index} className="space-y-1">
                                        <div className="flex justify-between items-center">
                                            <span className="font-medium text-sm">{skill.name}</span>
                                            <div className="flex items-center">
                                                <span className="text-xs text-gray-500 mr-2">{skill.level}%</span>
                                                {isEditing && (
                                                    <button
                                                        className="h-6 w-6 p-0 text-gray-400 hover:text-red-500"
                                                        onClick={() => removeSkill(index)}
                                                    >
                                                        <svg
                                                            xmlns="http://www.w3.org/2000/svg"
                                                            width="16"
                                                            height="16"
                                                            viewBox="0 0 24 24"
                                                            fill="none"
                                                            stroke="currentColor"
                                                            strokeWidth="2"
                                                            strokeLinecap="round"
                                                            strokeLinejoin="round"
                                                        >
                                                            <line x1="18" y1="6" x2="6" y2="18"></line>
                                                            <line x1="6" y1="6" x2="18" y2="18"></line>
                                                        </svg>
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                                <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${skill.level}%` }}></div>
                                            </div>
                                            {isEditing && (
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={skill.level}
                                                    onChange={(e) => handleSkillLevelChange(index, Number.parseInt(e.target.value))}
                                                    className="w-full h-2"
                                                />
                                            )}
                                        </div>
                                    </div>
                                ))}

                                {isEditing && (
                                    <div className="mt-4 pt-4 border-t">
                                        <h4 className="text-sm font-medium mb-2">Add New Skill</h4>
                                        <div className="flex gap-2">
                                            <input
                                                placeholder="Skill name"
                                                value={newSkill.name}
                                                onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })}
                                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400"
                                            />
                                            <div className="w-24 flex items-center gap-2">
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max="100"
                                                    value={newSkill.level}
                                                    onChange={(e) => setNewSkill({ ...newSkill, level: Number.parseInt(e.target.value) })}
                                                    className="w-full"
                                                />
                                                <span className="text-xs w-8">{newSkill.level}%</span>
                                            </div>
                                            <button
                                                onClick={addSkill}
                                                className="px-2 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                                            >
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    width="16"
                                                    height="16"
                                                    viewBox="0 0 24 24"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    strokeWidth="2"
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                >
                                                    <circle cx="12" cy="12" r="10"></circle>
                                                    <line x1="12" y1="8" x2="12" y2="16"></line>
                                                    <line x1="8" y1="12" x2="16" y2="12"></line>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {!isEditing && profileData.skills.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {profileData.skills.map((skill, index) => (
                                            <span
                                                key={index}
                                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                                            >
                                                {skill.name}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile
