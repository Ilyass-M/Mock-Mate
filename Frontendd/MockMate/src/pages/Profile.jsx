"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../context/AuthContext"
import axios from "axios"
import {toast} from "sonner"
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
    const [newSkill, setNewSkill] = useState({ name: "" })


    const url = "http://localhost:8000"
    const get_user_data = async () => {
        try {
            const response = await axios.get(url + "/api/user/", { withCredentials: true })
            const skills = await axios.get(url + "/api/skills/", { withCredentials: true })
            console.log("User data fetched successfully:", response.data)
            response.data.skills = skills.data
            return response.data
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
                    skills: data.skills || []
                })
            }
        })

    }, [])
    useEffect(() => {
        if (success) {
            const timer = setTimeout(() => {
                setSuccess(null)
            }, 3000)
            return () => clearTimeout(timer)
        }
        if (error) {
            const timer = setTimeout(() => {
                setError(null)
            }
                , 3000)
            return () => clearTimeout(timer)
        }
    }, [success, error])
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
    const addskilltocandidate = async (skill) => {
        try {

            const response = await axios.post(url + "/api/skills/", { "skill": skill }, { withCredentials: true })
            if (response.status === 200) {
                console.log("Skill added successfully:", response.data)
                setSuccess("Skill added successfully!")
            } else {
                console.error("Error adding skill:", response)
                setError("Failed to add skill. Please try again.")
            }
        } catch (error) {
            console.error("Error adding skill:", error)

            setError("Failed to add skill. Please try again.")
        }
    }
    const addSkill = () => {
        for (const skill of profileData.skills) {
            if (skill.trim().toLowerCase() === newSkill.name.trim().toLowerCase()) {
                toast.error("Skill already exists.")
                setError("Skill already exists.")
                return
            }
        }
        if (newSkill.name.trim()) {
            setProfileData((prevData) => ({
                ...prevData,
                skills: [...prevData.skills, { name: newSkill.name, level: 0 }],
            }))
            setNewSkill({ name: "" })
        }
        addskilltocandidate(newSkill.name)
    }
    const handleskilldelete = async (skill) => {
        try {
            // Using query parameters to specify which skill to delete
            const response = await axios.delete(url + `/api/skills/?skill=${encodeURIComponent(skill)}`, { withCredentials: true })
            if (response.status === 200) {
                console.log("Skill deleted successfully:", response.data)
                setSuccess("Skill deleted successfully!")
            } else {
                console.error("Error deleting skill:", response)
                setError("Failed to delete skill. Please try again.")
            }
        }
        catch (error) {
            console.error("Error deleting skill:", error)
            setError("Failed to delete skill. Please try again.")
        }
    }

    const removeSkill = (index) => {
        setProfileData((prevData) => ({
            ...prevData,
            skills: prevData.skills.filter((_, i) => i !== index),
        }))
        handleskilldelete(profileData.skills[index])
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
                <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
                    {/* Left Column - Profile Picture & Basic Info */}


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
                                        className="px-3 py-1 border border-gray-300 rounded-md text-sm flex items-center gap-1 text-white    hover:bg-gray-50 transition-colors"
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
                                            className="px-3 text-white py-1 border border-gray-300 rounded-md text-sm flex items-center gap-1 hover:bg-gray-50  bg-red-800"
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
                                        <label htmlFor="fullname" className="block text-sm font-medium text-gray-700 mb-1 text-left">
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
                                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1 text-left">
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
                                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1 text-left">
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
                                        <label htmlFor="phone_number" className="text-left block text-sm font-medium text-gray-700 mb-1">
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
                            </div>                            <div className="space-y-4">
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                    {profileData.skills.map((skill, index) => (
                                        <div
                                            key={index}
                                            className="bg-indigo-50 rounded-lg p-3 relative shadow-sm border border-indigo-100"
                                        >
                                            <div className="font-medium text-indigo-800">{skill}</div>
                                            {isEditing && (
                                                <button
                                                    className="text-white"
                                                    onClick={() => removeSkill(index)}
                                                    title="Remove skill"
                                                >
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="14"
                                                        height="14"
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
                                    ))}

                                    {isEditing && (
                                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 flex flex-col items-center justify-center min-h-[80px]">
                                            <div className="flex flex-col w-full gap-2">
                                                <input
                                                    placeholder="Add a new skill"
                                                    value={newSkill.name}
                                                    onChange={(e) => setNewSkill({ name: e.target.value })}
                                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 text-sm"
                                                />
                                                <button
                                                    onClick={addSkill}
                                                    disabled={!newSkill.name.trim()}
                                                    className="px-3 py-1.5 bg-indigo-600 text-white rounded-md hover:bg-indigo-700  transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed text-sm w-full flex items-center justify-center gap-1"
                                                >
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="14"
                                                        height="14"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    >
                                                        <line x1="12" y1="5" x2="12" y2="19"></line>
                                                        <line x1="5" y1="12" x2="19" y2="12"></line>
                                                    </svg>
                                                    Add Skill
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {!isEditing && profileData.skills.length === 0 && (
                                    <div className="text-center py-6 text-gray-500">
                                        No skills added yet. Click Edit to add skills.
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
