<template>
    <div>
        <div v-if="isTagDisallowed" class="CardContainer">
            <div class="CardType" @mouseenter="changeCardStyle($event)" @mouseleave="removeCardStyle($event)">
                <!---->
                <el-image fit="fill"
                    style="width: 100%;height:62%;border-radius: 10px 10px 0 0;box-shadow: rgba(50, 50, 93, 0.25) 0px 2px 5px -1px, rgba(0, 0, 0, 0.3) 0px 1px 3px -1px;"
                    :src="'image?id='+imageId">
                    <div slot="error" class="image-slot">
                        <img fit="fill"
                            style="width: 100%;height:62%;border-radius: 10px 10px 0 0;box-shadow: rgba(50, 50, 93, 0.25) 0px 2px 5px -1px, rgba(0, 0, 0, 0.3) 0px 1px 3px -1px;"
                            src="@/assets/404_images/error.png" />
                    </div>
                </el-image>
                <el-row style="margin-top: 10px;">
                    <el-col :span="17">
                        <h5
                            style="font-size:5px;font-weight: revert;text-align: left;margin-left: 4%;margin-top: 2%;color: #909399;margin-bottom: 0">
                            Enjoy it!
                        </h5>
                    </el-col>
                    <el-col :span="3">
                        <!--收藏图片-->
                        <el-tooltip class="item" effect="dark" :content="isCollectedLoading? 'waiting...' :
                    (isCollected ? 'Don\'t collect it': 'Collect it')
                    " placement="top-start">
                            <div v-if="!isCollectedLoading">
                                <em :class="isCollected? 'el-icon-star-on': 
                            'el-icon-star-off'" style="font-size: 20px;" @click="collectImage"></em>
                            </div>
                            <div v-else>
                                <em class="el-icon-loading" style="font-size: 20px"></em>
                            </div>

                        </el-tooltip>

                    </el-col>
                    <el-col :span="3">
                        <!--查看大图-->
                        <el-tooltip class="item" effect="dark" content="Enjoy it" placement="top-start">
                            <em class="el-icon-zoom-in" style="font-size: 20px;" @click="viewBigImage"></em>
                        </el-tooltip>
                    </el-col>
                </el-row>
                <h4 style="text-align: left;margin-left: 2%;margin-top: 5px;margin-right: 4%;margin-bottom: 0">
                    Image{{imageId}}
                </h4>
                <div class="label-list">
                    <el-tag type="primary" v-for="(i,index) in showTags" :key="index" effect="dark"
                        :color="labelColor[index]" :hit="true">
                        {{i}}
                    </el-tag>
                </div>

                <el-dialog :visible.sync="dialogVisible">
                    <img width="80%" height="80%" :src="'image?id='+imageId" alt="">
                </el-dialog>

            </div>
        </div>
    </div>

</template>

<script>
import axios from 'axios';

export default{
    name: 'ImageCard',

    data() {
        return {
            colors: ['#a3c6ea', '#70a8c4', '#559bcb'],
            labelColor:["#77C9D4","#57BC90","#015249"],
            imageSource: '',
            isMouseOn: false,
            tags: [],
            isCollected: false,
            dialogVisible: false,
            isCollectedLoading: false,
        }
    },

    computed:{
        showTags(){
            if (this.tags.length != 0) {
                return this.tags.slice(0,3)
            } else {
                return ['none']
            }
        },
        isTagDisallowed() {
            if (!this.hideTags) {
                return true;
            }
            for (let i = 0; i < this.tags.length; ++i) {
                if (this.disallowedTags.indexOf(this.tags[i]) != -1) {
                    return false;
                }
            }
            return true;
        }
    },

    props:{
        imageUrl: String,
        imageId: String,
        disallowedTags: Array,
        hideTags: Boolean,
    },

    created(){
        // 获取图片详细信息
        axios({
            method: 'get',
            url: 'info',
            params: {
                id: this.imageId,
            }
        }).then(response => {
            this.isCollected = response.data.isCollected;
            this.tags = response.data.tags;
        }).catch(() => {

        })
    },

    methods: {
        changeCardStyle(e){
            e.currentTarget.className='activeMe';
            this.isMouseOn = true;
        },
        removeCardStyle(e){
            e.currentTarget.className='CardType';
            this.isMouseOn = false;
        },
        collectImage() {
            this.isCollectedLoading = true;

            axios({
                method: 'get',
                url: 'collect',
                params: {
                    id: this.imageId,
                }
            }).then(() => {
                setTimeout(() => {
                    
                    this.isCollected = !this.isCollected;
                    if (this.isCollected) {
                        this.$message({
                            message: 'You collect it successfully!',
                            type: 'success'
                        });
                    } else {
                        this.$message({
                            message: 'You remove it from collection successfully!',
                            type: 'success'
                        });
                    }
                    this.isCollectedLoading = false;
                }, 600);
            }).catch(() => {
                this.isCollectedLoading = false;
            }).finally(()=> {
                this.$emit('changeCollect');
            })
        },
        viewBigImage() {
            this.dialogVisible = true;
        },
        
    }
}
</script>

<style>


.CardType {
    width: 95%;
    height: 95%;
    margin: 0 auto;
    margin-top: 5px;
    border-radius: 10px !important;
    box-shadow: rgba(0, 0, 0, 0.1) 0px 20px 25px -5px, rgba(0, 0, 0, 0.04) 0px 10px 10px -5px !important;
    background-color: rgba(229, 225, 225, 0.34);
    cursor: pointer;
    -webkit-transition: all 200ms ease-in;
}

.activeMe {
    width: 95%;
    height: 95%;
    margin: 0 auto;
    margin-top: 0px;
    border-radius: 10px !important;
    box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px !important;
    background-color: rgba(255, 255, 255, 0.84);
    cursor: pointer;
    -webkit-transition: all 200ms ease-in;
}

.UserAvatar {
    width: 54px;
    height: 54px;
    border-radius: 27px;
    box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;
    margin-left: 30%;
}
</style>

<style scoped>
.el-divider--vertical {
    height: 4em !important;
    width: 1.5px !important;
}

.icon-love{
    position: absolute;
    left: 40%;
    bottom: 40%;
}

/* 标签列表 */
.label-list{
    padding:1px 1px;
    margin:1px 1px ;
}
.el-tag{
    float:left;
    white-space: pre-line;
    word-break: break-all;
    margin-top: 5px;
    margin-left: 5px;
    max-height: 4vh;
    color:white;
}


.CardContainer {
    width: 270px;
    height: 290px;
    margin-bottom: 20px;
    margin-left: 25px;
}
</style>